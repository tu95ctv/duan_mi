 # -*- coding: utf-8 -*-
import re
import xlrd
# import time
# from unidecode import unidecode
# import xlwt
# from collections import  OrderedDict
# import operator


from odoo.exceptions import UserError
import base64
from copy import deepcopy


# import sys
# VERSION_INFO   = sys.version_info[0]

from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import gen_model_dict
from xlutils.copy import copy




### new ##


from odoo.addons.dai_tgg.models.model_dict_folder.tool_tao_instance import read_excel_cho_field,check_is_string_depend_python_version,empty_string_to_False,get_key#,get_width,header_bold_style,VERSION_INFO
from odoo.addons.downloadwizard.models.dl_models.dl_model  import wrap_center_vert_border_style
from odoo.addons.dai_tgg.models.model_dict_folder.get_or_create_func import get_or_create_object_has_x2m
from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import muon_xuat_dac_tinh_gi,ordered_a_model_dict,recursive_add_model_name_to_field_attr,define_col_index,define_col_index,check_xem_att_co_nam_ngoai_khong,write_get_or_create_title,check_col_index_match_xl_title,rut_gon_key
# from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import tim_type_cua_attr
MAP_TYPE = {
                      'integer':[int,float],
                      'float':float, 
                      'many2one':int,
                      'char':str,
                      'selection':str,
                      'text':str, 
                      'boolean':bool,
                      'many2many':list,
                      'one2many':list,
                      
                      
                      }

# def check_type(val,field_type):
#     if val != False:
#         try:
#             type_tuong_ung_voi_char_field_type = MAP_TYPE[field_type]
#         except:
#             raise UserError('')
#         isinstance(object, type_tuong_ung_voi_char_field_type)

#####################vkjzkldjfklsdjfkldsjf
def replace_val_for_ci(field_attr,key_tram,val,needdata):
    
    
    #### deal replace string ####
    replace_string = get_key( field_attr,'replace_string')
    if  replace_string and check_is_string_depend_python_version(val):
        for pattern,repl in replace_string:
            pattern = pattern.replace('(','\(').replace(')','\)')
            val = re.sub(pattern, repl, val)
    #### end  deal replace string ####
    
    
    
    #### deal empty val ###
    empty_val = get_key( field_attr,'empty_val')
    if empty_val and val in empty_val:
        val = False   
    #### !!!deal empty val ###
    
    
    
    
    #### deal  replace val#####
    replace_val = get_key( field_attr,'replace_val')
    if replace_val:
        replace_val_tuple = replace_val.get(needdata['sheet_name']) or replace_val.get('all')
        if replace_val_tuple:
            for k,v in replace_val_tuple:
                if val ==k:
                    val = v
                    break
    #### !!!deal  replace val#####
                
    ### deal defautl ###
    if val == False and  field_attr.get('default') !=None:
        val = field_attr.get('default')
    
    ### !!!!deal defautl ###
    return val
def check_type_of_val(field_attr,val,field_name,model_name):        
    if field_attr.get('bypass_check_type'):
        return True
    field_type = field_attr.get('field_type')
#     check_field_type = field_attr.get('check_field_type',True)
    if field_type:
        type_allow = field_attr.get('type_allow',[])
        if val != False and val != None:
            try:
                type_tuong_ung_voi_char_field_type = MAP_TYPE[field_type]
            except:
                return True
                raise UserError(u'không có field_type:%s này'%field_type)
            if field_attr.get('is_x2m_field'):
                type_tuong_ung_voi_char_field_type = list
            if isinstance( type_tuong_ung_voi_char_field_type,list):
                type_allow.extend(type_tuong_ung_voi_char_field_type)
            else:
                type_allow.append(type_tuong_ung_voi_char_field_type)
            pass_type_check = False
            for a_type_allow in type_allow:
                if isinstance(val, a_type_allow):
                    pass_type_check = True
                    continue
            if not pass_type_check:
                raise UserError(u'model: %s- field:%s có giá trị: %s, đáng lẽ là field_type:%s nhưng lại có type %s'%(model_name, field_name,val,field_type,type(val)))
#     else:
#         raise UserError(u'Không có field_type:%s trong biến MAP_TYPE'%(field_type))      
def read_val_for_ci(self,model_name, field_name, set_val,col_index,
                    a_field_vof_dict,
                    MODEL_DICT,
                    field_attr,
                    sheet,row,
                    merge_tuple_list,
                    check_file,
                    needdata,
                    noti_dict,
                    key_tram,
                    sheet_of_copy_wb,
                    setting,
#                     collect_all_field_dict
                    ):  
    
    ### end  deal skip_field_cause_first_import####
    val = False
    obj = False



    if set_val != None:
        val = set_val
#         if MODEL_DICT.get('print_write_dict_new',False):
#             print ('***set_val',set_val)
    elif col_index !=None: # đọc file exc
        xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
        a_field_vof_dict['excel_val'] = xl_val
        val = empty_string_to_False(xl_val)
#         if val != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('is_x2m_field'):
        if val != False and field_attr.get('is_x2m_field'):
            val = val.split(',')
            val = list(map(lambda i: empty_string_to_False(i.strip()),val))
            for i in val:
                if i==False:
                    raise UserError(u'Không được = False')
                
        print ('excel read model_name:%s field_name:%s'%(model_name,field_name),'xl_val',xl_val,'val',xl_val)
    
    elif field_attr.get('fields') :
        exist_val_before_loop_fields_func =   field_attr.get('exist_val_before_loop_fields_func')
        if exist_val_before_loop_fields_func:
            cho_phep_exist_val_before_loop_fields_func = field_attr.get('cho_phep_exist_val_before_loop_fields_func') if 'cho_phep_exist_val_before_loop_fields_func' in field_attr else setting.get('cho_phep_exist_val_before_loop_fields_func')
            exist_val_before_loop_fields_func = cho_phep_exist_val_before_loop_fields_func and exist_val_before_loop_fields_func
      
        if exist_val_before_loop_fields_func:
            exist_val = exist_val_before_loop_fields_func(needdata,self) #1,True ; F,False
        else:
            exist_val = False
        
        
#         exist_val_search_only = True
        if exist_val:
            write_when_val_exist = setting['write_when_val_exist']
            check_excel_obj_is_exist_func = field_attr.get('check_excel_obj_is_exist_func') 
            check_excel_obj_is_exist_func =   setting.get('allow_check_excel_obj_is_exist_func') and check_excel_obj_is_exist_func
#             if write_when_val_exist:
#                 exist_val_search_only = False
# #                 if check_excel_obj_is_exist_func:
# #                     is_search = True
# #                 else:
# #                     is_search = False
#             else:
#                 exist_val_search_only = True
#         else:
#             exist_val_search_only = False

        
        
        
        
        
        
        

        if not exist_val or (exist_val and (check_excel_obj_is_exist_func or write_when_val_exist)) or check_file:
            
          
            if check_file:
                is_search = True
                is_create = False
                is_write = False
                
            else:
                if exist_val:
                    if write_when_val_exist:
                        is_create = False
                        is_write = True
                    else:
                        is_create = False
                        is_write = False
                    if check_excel_obj_is_exist_func:
                        is_search = True
                    else:
                        is_search = False
                    
                        
                else:
                    is_create = True
                    is_write = True
                    is_search =True
            
            obj,val, get_or_create  = create_instance (self, field_attr,sheet, 
                                                                    row, 
                                                                    merge_tuple_list,
                                                                    needdata, 
                                                                    noti_dict,
                                                                    key_tram=key_tram, 
                                                                    check_file = check_file ,
                                                                    sheet_of_copy_wb = sheet_of_copy_wb,
#                                                                     exist_val_search_only = exist_val_search_only,  
                                                                    exist_val = exist_val,
                                                                    setting=setting,
                                                                    is_search = is_search,
                                                                    is_create = is_create,
                                                                    is_write = is_write,
                                                                   )

        if exist_val:
            if  check_excel_obj_is_exist_func:# and not get_or_create:,not write_when_val_exist and
                try:
                    check_excel_obj_is_exist_func(get_or_create, obj, exist_val)
                except UserError as e:
                    if setting ['allow_check_excel_obj_is_exist_raise_or_break'] =='break':
                        return False,False,'break'
                    else:
                        raise UserError(e.args)
                        
#                         print ('ahahaha')
#                         raise UserError(e.args)
            val= exist_val.id
            obj = exist_val
            get_or_create = True
            this_model_notice = noti_dict.setdefault(field_attr.get('model'),{})
            this_model_notice['exist_val'] = this_model_notice.get('exist_val',0) + 1
        a_field_vof_dict['get_or_create'] = get_or_create
        if check_file:
            if val ==False or val ==None:# ke qua search la rỗng obj (None,None,False) (obj(),False,False)
#                 if field_attr.get('key') == True:
                val = None
            offset_write_xl = get_key(field_attr, 'offset_write_xl')
            if offset_write_xl !=None:
                if get_or_create:
                    get_or_create_display = u'Đã Có' 
                else:
                    if field_attr['fields']['name']['val'] !=False:
                        get_or_create_display = u'Chưa'
                    else:
                        get_or_create_display = u'empty cell'
                sheet_of_copy_wb.write(row,sheet.ncols + offset_write_xl , get_or_create_display,wrap_center_vert_border_style)
    return obj,val,True      
#F1 
def get_a_field_val(self,field_name,field_attr,key_tram,
                            needdata,row,sheet,
                            MODEL_DICT,
                           check_file,
#                            workbook_copy,
                           sheet_of_copy_wb,
                           merge_tuple_list,model_name,
#                            main_call_create_instance_model,
                           noti_dict,
                           key_search_dict,update_dict,x2m_fields,
                           collect_all_field_dict,
                           setting
                           ):
#     instance_false = False
    skip_this_field = get_key(field_attr, 'skip_this_field', False)
    if callable(skip_this_field):
            skip_this_field = skip_this_field(self)
    if skip_this_field:
            return 'continue'
    col_index = get_key(field_attr, 'col_index')
    a_field_vof_dict = field_attr # them 3
    ###  deal set_val ########
    set_val = get_key( field_attr,'set_val')
    func = get_key( field_attr,'func')
    #F11
    obj,val,code = read_val_for_ci(self,model_name,field_name,set_val,col_index,
                    a_field_vof_dict,
                    MODEL_DICT,
                    field_attr,sheet,row,
                    merge_tuple_list,
                    check_file,
                    needdata,noti_dict,key_tram,
#                     workbook_copy,
                    sheet_of_copy_wb,
                    setting,
#                     collect_all_field_dict
                    )
    if code =='break':
        return 'break_because_required'
    a_field_vof_dict['before_func_val'] = val
    # func
    karg = get_key( field_attr,'karg',{})
    if karg ==None:
        karg ={}
    func_pre_func = field_attr.get('func_pre_func')
    if func_pre_func:
        val = func_pre_func(val, needdata,self)
    if func:
        try:
            val = func(val, needdata,**karg)
        except TypeError:
            try:
                val = func(val, needdata,self,**karg)
            except TypeError:
                val = func(val,**karg)
        print ('func read model_name:%s field_name:%s'%(model_name,field_name),'val',val)
    #end func
    
    
    val =replace_val_for_ci(field_attr,key_tram,val,needdata)
    a_field_vof_dict['val'] = val
    a_field_vof_dict['obj'] = obj
    
    
    
    
  
        
    
    if check_file:     
#         if val == None:
#             collect_all_field_dict['instance_false'] = True
        required_when_normal  = get_key(field_attr, 'required', False)   
        required   = get_key(field_attr, 'required_not_create', required_when_normal) 
        if (required_when_normal and val==False) and required ==False:
            collect_all_field_dict['instance_false'] = True
    else:
        required = get_key(field_attr, 'required', False)  
#         required = False if bypass_this_field_if_value_equal_False else required

#         required = required and not bypass_this_field_if_value_equal_False
            
    #### !!! deal required #####    
    
    
   
    key_or_not = field_attr.get('key')
    if callable(key_or_not):
        key_or_not = key_or_not(needdata)
    bypass_this_field_if_value_equal_False = get_key(field_attr, 'bypass_this_field_if_value_equal_False', setting['bypass_this_field_if_value_equal_False_default'])
    if bypass_this_field_if_value_equal_False and val==False: 
        return 'continue'
    elif required and (val==False and isinstance(val, bool)):# val ==False <==> val ==0, val ==0 <==> val =False
#         if field_attr.get('raise_if_False'):
#             raise UserError('raise_if_False field: %s'%field_name)
#         if main_call_create_instance_model :#or MODEL_DICT.get('print_write_dict_new',False)
#             print (u'skip việc get or create của dòng này because required but,model %s- field %s, val:%s'%(model_name,field_name,val))
        this_model_notice = noti_dict.setdefault(model_name,{})
        skip_because_required = this_model_notice.setdefault('skip_because_required',0)
        this_model_notice['skip_because_required'] = skip_because_required + 1
        return 'break_because_required' #sua 5
    
    elif not field_attr.get('for_excel_readonly'):
        
        if key_or_not==True:
            key_search_dict [field_name] = val
        elif key_or_not == 'Both':
            key_search_dict [field_name] = val
            update_dict [field_name] = val
        else:
            update_dict [field_name] = val
#         print ('4',count)


    valid_field_func = field_attr.get('valid_field_func')
    if valid_field_func:
        valid_field_func(val,obj,needdata,self)
    
    
    
    
        
    print ("row: ", row,'model_name: ',model_name,'-field: ', field_name, '-val: ', val)
    check_type_of_val(field_attr,val,field_name,model_name)
    
    if field_attr.get('is_x2m_field'):
            x2m_fields.append(field_name)
            collect_all_field_dict['remove_all_or_just_add_one_x2m'] &= field_attr.get('remove_all_or_just_add_one_x2m',True)
#     return instance_false
    return False        
#F2
def get_or_create_instance_from_key_search_and_update_dict(self,
                           model_name,
                           key_search_dict,
                           update_dict,
                           check_file,
#                            instance_false,
                           noti_dict,
                           inactive_include_search,
                           x2m_fields,
                           remove_all_or_just_add_one_x2m,
                           MODEL_DICT,key_tram,
#                            mode_no_create_in_main_instance,
#                            exist_val_search_only=False,
                           exist_val = False,
#                            search_func_para={},
                           setting={},
                           is_search = True,
                           is_create = True,
                           is_write = True,#                            collect_all_field_dict={}
                           ):
    if key_search_dict or MODEL_DICT.get('search_func'):
        if MODEL_DICT.get('not_get_or_create'):
            return False,False, False
#         if MODEL_DICT.get('print_write_dict_new',False):
#         if model_name == 'stock.production.lot':
#             raise UserError ('key_search_dict của model %s: %s'%(model_name,key_search_dict))
            
        
        obj,obj_val, get_or_create = get_or_create_object_has_x2m(self, model_name,
                                                                   key_search_dict, 
                                                                   update_dict,
#                                 is_must_update = True, 
                                noti_dict = noti_dict,
                                inactive_include_search  = inactive_include_search, 
                                x2m_field = x2m_fields[0] if x2m_fields else False,
                                remove_all_or_just_add_one_x2m=remove_all_or_just_add_one_x2m,
#                                 is_return_get_or_create = True,
                                model_dict=MODEL_DICT,
                                key_tram = key_tram,
#                                 only_search = check_file or exist_val_search_only,
                                exist_val=exist_val,
#                                 search_func_para=search_func_para,
                                setting=setting,
#                                 collect_all_field_dict=collect_all_field_dict
                                check_file=check_file,
                                is_search = is_search,
                                is_create = is_create,
                                is_write = is_write,
                                
                                )
        return obj,obj_val, get_or_create 
    else:
        raise UserError(u'Không có Key search dict, model_name%s'%model_name)
#         return False,False,False  

################# CREATE INSTANCE
def create_instance (self, MODEL_DICT,
                    sheet, row,
                     merge_tuple_list,
                     needdata, noti_dict, 
                     main_call_create_instance_model = False,
                    key_tram=None, 
                    check_file = False,
                    sheet_of_copy_wb = False,
#                     mode_no_create_in_main_instance = False,
#                     exist_val_search_only = False,
                    setting={},
                    exist_val = False,
                    is_search = True,
                    is_create = True,
                    is_write = True,
#                     search_func_para={},
                     ):
        
    key_search_dict = {}
    update_dict = {}
    model_name = get_key(MODEL_DICT, 'model')
    x2m_fields = []
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    collect_all_field_dict = {'remove_all_or_just_add_one_x2m':True}#'instance_false':False,'
    break_condition = False
    for field_name,field_attr  in MODEL_DICT['fields'].items():
        code = get_a_field_val(self,field_name,field_attr,key_tram,needdata,row,sheet,
                           MODEL_DICT,
                           check_file,
                           sheet_of_copy_wb,
                           merge_tuple_list,
                           model_name,
#                            main_call_create_instance_model,
                           noti_dict,
                           key_search_dict,
                           update_dict,
                           x2m_fields,
                           collect_all_field_dict,
                           setting)
        if code =='break_because_required':
            break_condition = True# moi them
            if field_attr.get('raise_if_False'):
                raise UserError('raise_if_False field: %s'%field_name)
            if main_call_create_instance_model :#or MODEL_DICT.get('print_write_dict_new',False)
                print (u'skip việc get or create của dòng này because required but,model %s- field %s'%(model_name,field_name))
            break
    if break_condition:
        if main_call_create_instance_model:
            if  True:#getattr(self, 'allow_cate_for_ghi_chu',False):
                break_condition_func_for_main_instance  = get_key(MODEL_DICT,'break_condition_func_for_main_instance')
                if break_condition_func_for_main_instance:
                    break_condition_func_for_main_instance(needdata)
        obj_val = False
        get_or_create = False
        return False, obj_val,get_or_create
    if collect_all_field_dict.get('instance_false'):
        return None,None,False
    
    last_record_function = get_key(MODEL_DICT, 'last_record_function')
    if last_record_function:
        last_record_function(needdata,self)
    
    if main_call_create_instance_model:
        pass
        print ('key_search_dict',key_search_dict)
        print ('update_dict',update_dict)
    
    
    obj,obj_val, get_or_create  = get_or_create_instance_from_key_search_and_update_dict(
                                                   self,
                                                   model_name,
                                                   key_search_dict,
                                                   update_dict,
                                                   check_file,
#                                                    collect_all_field_dict['instance_false'],
                                                   noti_dict,
                                                   inactive_include_search,
                                                   x2m_fields,
                                                   collect_all_field_dict['remove_all_or_just_add_one_x2m'],
                                                   MODEL_DICT,
                                                   key_tram,
#                                                    mode_no_create_in_main_instance,
#                                                    exist_val_search_only=exist_val_search_only,
                                                   exist_val=exist_val,
#                                                    search_func_para=search_func_para,
                                                   
                                                   
                                                    setting=setting,
                                                    is_search = is_search,
                                                    is_create = is_create,
                                                    is_write = is_write,
#                                                    collect_all_field_dict=collect_all_field_dict
                                                   )
    return obj,obj_val, get_or_create 
def check_notice_dict_co_create_or_get(model_name,noti_dict,check_file,not_get_or_create):
    adict = noti_dict.get(model_name,{})
    if not adict.get('create') and not adict.get('update') and not check_file and not not_get_or_create:
        raise UserError(u'các row bị bỏ qua hết không có dòng nào được tạo hoặc được update')
    

def importthuvien(odoo_or_self_of_wizard,
                  model_dict = False,
                  key=False,
                  key_tram=False,
                  check_file = False,
                  mode=u'1'):
    self = odoo_or_self_of_wizard
    
    
    
    self_key_tram =  getattr(self,'key_tram',False) or key_tram

    
    if not model_dict:
        ALL_MODELS_DICT = gen_model_dict(self=self, 
                                         key_tram = self_key_tram,mode=mode)
    else:
        ALL_MODELS_DICT =  model_dict
    
#     for r in self:
    if not self.file:
        raise UserError(u'Bạn phải upload file để import')
    file_content = base64.decodestring(self.file)
    if '.xlsx' in self.filename:
        formatting_info = False
    else:
        formatting_info = True
    xl_workbook = xlrd.open_workbook(file_contents = file_content, formatting_info=formatting_info)
    noti_dict = {}
#     noti_dict['skip because required'] = 0
    if not key:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[self.type_choose]
    else:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[key]
    context = {'from_import':True} 
    context_get = CHOOSED_MODEL_DICT.get('context')
    if context_get:
        context.update(context_get)
    self = self.with_context(context)
   
    
    key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
    key_tram = key_allow and self_key_tram
    if key_allow and not key_tram:
        raise UserError(u'ban phai chon key_tram')
    #R2
    mode_no_create_in_main_instance = getattr(self,'mode_no_create_in_main_instance',None)
    rut_gon_key(CHOOSED_MODEL_DICT,key_tram,mode_no_create_in_main_instance=mode_no_create_in_main_instance)
    print ('***CHOOSED_MODEL_DICT***',CHOOSED_MODEL_DICT)
    
    #R1
    ordered_a_model_dict( CHOOSED_MODEL_DICT)
    
    #R3
    recursive_add_model_name_to_field_attr(self,CHOOSED_MODEL_DICT,key_tram=key_tram)
#     dac_tinhs = {}
#     xuat_het_dac_tinh(CHOOSED_MODEL_DICT,key_tram,dac_tinhs)
#     self.test_result_2 =u'kaka %s'% dac_tinhs 
#     return False

#     ghom_dac_tinh = {}
#     rs = muon_xuat_dac_tinh_gi(CHOOSED_MODEL_DICT,attr_muon_xuats = ['skip_this_field'],ghom_dac_tinh=ghom_dac_tinh)
#     self.test_result_1 = rs
#     return False
#     self.test_result_1 = ghom_dac_tinh

    #R3 check_xem_att_co_nam_ngoai_khong
#     check_xem_att_co_nam_ngoai_khong(CHOOSED_MODEL_DICT,key_tram)

    
    sheet_names = get_key(CHOOSED_MODEL_DICT, 'sheet_names')
    if callable(sheet_names):
        try:
            sheet_names = sheet_names(self)
        except TypeError as e:
            if 'required positional argument' in u'%s'%e:
                try:
                    sheet_names = sheet_names(self,xl_workbook)
                except TypeError as e:
                    if 'required positional argument' in u'%s'%e:
                        sheet_names = sheet_names(self,xl_workbook,mode)
                    else:
                        raise UserError(u'có 1 lỗi ở hàm sheet_names: %s '%e)
            else:
                        raise UserError(u'có 1 lỗi ở hàm sheet_names: %s '%e)    
    needdata = {}
    needdata['sheet_names'] = sheet_names
    needdata['key_tram'] = key_tram
    


    
    setting = CHOOSED_MODEL_DICT.get('setting',{})
    setting.setdefault('allow_write_from_False_to_not_false',True)
        
#     if hasattr(self, 'not_update_field_if_instance_exist_default'):
#         not_update_field_if_instance_exist_default =  self.not_update_field_if_instance_exist_default
#     else:
#         not_update_field_if_instance_exist_default = CHOOSED_MODEL_DICT.get('not_update_field_if_instance_exist_default',False)
#     
#     
#     setting['not_update_field_if_instance_exist_default'] = not_update_field_if_instance_exist_default
    
#     if hasattr(self, 'bypass_this_field_if_value_equal_False_default'):
#         bypass_this_field_if_value_equal_False_default =  self.bypass_this_field_if_value_equal_False_default
#     else:
#         bypass_this_field_if_value_equal_False_default = CHOOSED_MODEL_DICT.get('bypass_this_field_if_value_equal_False_default',False)
   
    
    
    
    setting['bypass_this_field_if_value_equal_False_default'] =  CHOOSED_MODEL_DICT.get('bypass_this_field_if_value_equal_False_default',False)
    
    
    
    
    setting2 = CHOOSED_MODEL_DICT.get('setting2',{})
    if setting2:
        setting.update(setting2)
    setting.setdefault('allow_write',True)
#     if hasattr(self, 'not_allow_write'):
#         not_allow_write = getattr(self,'not_allow_write')
#     else:
#         not_allow_write = CHOOSED_MODEL_DICT.get('not_allow_write',False)
#     setting['allow_write'] = not not_allow_write
#     if hasattr(self, 'write_when_val_exist'):
#         write_when_val_exist =  self.write_when_val_exist
#     else:
#         write_when_val_exist = CHOOSED_MODEL_DICT.get('write_when_val_exist',True)
#     setting['write_when_val_exist'] = write_when_val_exist
#     
#     
#     if hasattr(self, 'allow_check_excel_obj_is_exist_func'):
#         allow_check_excel_obj_is_exist_func =  self.allow_check_excel_obj_is_exist_func
#     else:
#         allow_check_excel_obj_is_exist_func = CHOOSED_MODEL_DICT.get('allow_check_excel_obj_is_exist_func',True)
#     
#     setting['allow_check_excel_obj_is_exist_func'] = allow_check_excel_obj_is_exist_func
    
    
    
    
    
#     print ('**setting**',setting)
#     raise UserError(u'%s'%setting)
    prepare_func = CHOOSED_MODEL_DICT.get('prepare_func')
    if prepare_func:
        prepare_func(needdata,self)
    print ('sheet_names',sheet_names)
    for sheet_name in sheet_names:
        print ('**sheet_name',sheet_name)
        COPY_MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
        needdata['vof_dict'] = COPY_MODEL_DICT.get('fields') 
        needdata['sheet_name'] = sheet_name
#         needdata['key_tram'] = key_tram
#         if key_tram:
#             rut_gon_key(COPY_MODEL_DICT,key_tram)
        sheet = xl_workbook.sheet_by_name(sheet_name)
        #R3 xuat dac tinh
        if getattr(self,'dac_tinh',None):
            dt = self.dac_tinh.split(',')
            
            dactinh = muon_xuat_dac_tinh_gi(COPY_MODEL_DICT, attr_muon_xuats = dt,ghom_dac_tinh = {})
            print ('***dactinh',dactinh)
            self.test_result_1 =  dactinh
            self.test_result_2 =  COPY_MODEL_DICT
            if self.only_xuat_thuoc_tinh:
                if not dt:
                    raise UserError(u'bạn phải chọn thuộc tính gì đó')
                return False
        
        #R4 define_col_index
        
        largest_map_row_choosing = get_key(CHOOSED_MODEL_DICT, 'largest_map_row_choosing')#largest_map_row_choosing  is boolean
        range_1 = getattr(self, 'range_1',None)
        range_2 = getattr(self, 'range_2',None)
        
        if range_1 or range_2:
            title_rows = range(range_1,range_2)
        else:
        
            if largest_map_row_choosing:
#                 range_1 = range_1 or 0
#                 range_2 = range_2 or sheet.nrows
                title_rows = range(0,sheet.nrows)
            else:
                title_rows_some_sheets = CHOOSED_MODEL_DICT.get('title_rows_some_sheets',{})
                if title_rows_some_sheets:
                    title_rows_some_sheets=title_rows_some_sheets.get(sheet_name)
                if title_rows_some_sheets:
                    title_rows = title_rows_some_sheets
                else:
                    title_rows = get_key(CHOOSED_MODEL_DICT, 'title_rows')  # MODEL_DICT['title_rows']
        row_title_index,largest_map_row = define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram)
        if largest_map_row_choosing:
            row_title_index = largest_map_row
#         if row_title_index == None:
#             raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
        #!R4
        
        check_col_index_match_xl_title(self,COPY_MODEL_DICT,key_tram,needdata)
        off_set_row = get_key(CHOOSED_MODEL_DICT, 'begin_data_row_offset_with_title_row', 1)
        min_row = row_title_index + off_set_row
        first_row = min_row + getattr(self,'begin_row',0)
        print ('first_row','min_row',first_row,min_row)
        dong_test = getattr(self,'dong_test',None) or CHOOSED_MODEL_DICT.get('dong_test')
        if not dong_test:
            last_row = sheet.nrows
        else:
            last_row = first_row + dong_test
        if last_row > sheet.nrows:
            last_row =  sheet.nrows
        if first_row >  last_row :
            raise UserError(u'first_row >  last_row')
        
#         print ('***COPY_MODEL_DICT',COPY_MODEL_DICT)
        
       
        
        
        
        if check_file:
            workbook_copy = copy(xl_workbook)
            sheet_of_copy_wb = workbook_copy.get_sheet(0)
            write_get_or_create_title(CHOOSED_MODEL_DICT,sheet,sheet_of_copy_wb, row_title_index, key_tram)
            is_search = True
            is_create = False
            is_write = False
        else:
            is_search = True
            is_create = True
            is_write = True
            workbook_copy = None
            sheet_of_copy_wb = None
        #!R7
        
        
        merge_tuple_list =  sheet.merged_cells
#         if check_file:
#             raise UserError(u'kkakakaka check file')
        for number_row_count,row in enumerate(range(first_row, last_row)):
            print ('sheet_name*******',sheet_name,'row',row)
#             COPY_MODEL_DICT_old = deepcopy(COPY_MODEL_DICT)
            create_instance (self, COPY_MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                              main_call_create_instance_model=True,
                              key_tram=key_tram,
                              check_file = check_file,
                              sheet_of_copy_wb = sheet_of_copy_wb,
#                               mode_no_create_in_main_instance = mode_no_create_in_main_instance,
                              setting=setting,
                               is_search = is_search,
                                is_create = is_create,
                                is_write = is_write,
                               )
        model_name = get_key(COPY_MODEL_DICT, 'model')
        
#         check_notice_dict_co_create_or_get(model_name,noti_dict,CHOOSED_MODEL_DICT['not_get_or_create'],)
    if number_row_count:
        self.imported_number_of_row = number_row_count + 1
        
    
    last_import_function  = get_key(CHOOSED_MODEL_DICT,'last_import_function')
    if last_import_function:
        last_import_function(needdata,self)
    self.log= noti_dict
    return workbook_copy
    
            

            

