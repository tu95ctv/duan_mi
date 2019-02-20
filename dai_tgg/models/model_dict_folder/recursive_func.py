 # -*- coding: utf-8 -*-
from odoo.addons.dai_tgg.models.model_dict_folder.tool_tao_instance import get_key,get_width,VERSION_INFO,get_by_key_tram
from odoo.addons.downloadwizard.models.dl_models.dl_model  import header_bold_style
from collections import  OrderedDict
from odoo.exceptions import UserError
import re
import operator
from odoo import _
STRING_TYPE_DICT = {str:'str',bool:'bool',list:'list',dict:'dict',int:'int'}                 
TYPES_ATT_DICT = {
            'begin_data_row_offset_with_title_row' : {'types': ['int']} ,
            'bypass_this_field_if_value_equal_False' : {'types': ['bool']} ,
            'col_index' : {'types': ['int']} ,
            'empty_val' : {'types': ['list']} ,
            'field_type' : {'types': ['str']} ,
            'for_excel_readonly' : {'types': ['bool']} ,
            'func' : {'types': ['function', 'NoneType']} ,
#             'get_or_create_para' : {'types': ['NoneType','dict'],'default':{}} ,#not_use_key: chưa xài
            'karg' : {'types': ['NoneType','dict']} ,#khong_can_khai_bao_key
            'key' : {'types': ['bool','function','str']} ,
            'key_allow' : {'types': ['bool']} ,
            # 'key_ltk_dc' : {'types': ['list']} ,
            # 'key_tti_dc' : {'types': ['NoneType']} ,
            'largest_map_row_choosing' : {'types': ['bool']} ,
            'last_import_function' : {'types': ['function']} ,
            'last_record_function' : {'types': ['function']} ,
            'model' : {'types': ['str']} ,
#             'not_create' : {'types': ['bool']} ,
            'offset_write_xl' : {'types': ['NoneType','int']} ,
            'raise_if_False' : {'types': ['bool']} ,
            'replace_string' : {'types': ['list']} ,
            'replace_val' : {'types': ['dict']} ,
            'required' : {'types': ['bool']} ,
            'set_val' : {'types': ['NoneType', 'str', 'function'],'no_need_check_type':True} ,
            'sheet_allow_this_field_not_has_exel_col' : {'types': ['list']} ,
            'sheet_names' : {'types': ['function','list']} ,
            'skip_field_if_not_found_column_in_some_sheet' : {'types': ['bool', 'NoneType']} ,
            'skip_this_field' : {'types': ['NoneType', 'bool','function']} ,
            'string' : {'types': ['str']} ,
            'title_rows' : {'types': ['list'],'no_need_check_type':True} ,
            'title_rows_some_sheets' : {'types': ['dict']} ,
            'transfer_name' : {'types': ['str']} ,
            'xl_title' : {'types': ['str', 'list', 'NoneType']} ,
            'inactive_include_search':{'types':['bool']},
            'is_x2m_field':{'types':['bool']},
            'remove_all_or_just_add_one_x2m':{'types':['bool']},
            'break_condition_func_for_main_instance':{'types': [ 'function']} ,
            'type_allow':{'types':['list']},
            'for_create_another':{'types':['bool']},
            'only_get':{'types':['bool']},
            'required_not_create':{'types':['bool']},
            'write_func':{'types': ['function']},
            'mode_no_create_in_main_instance':{'types': ['bool']},
            'skip_this_field_for_mode_no_create':{'types': ['bool']}, # no create in main instance
            'required_force':{'types': ['bool']},
            'bypass_check_type':{'types':['bool']},
            'dong_test':{'types':['int']},
            'set_val_instead_loop_fields':{'types': ['NoneType', 'str', 'function'],'no_need_check_type':True}
            
#             'skip_field_default':{'types': ['bool']}
}
###R1
def ordered_a_model_dict(model_dict):
    fields = model_dict['fields']
#     print ('fields',fields)
    for fname,attr in fields:
        if attr.get('fields'):
            new_ordered_dict = ordered_a_model_dict(attr)
    model_dict['fields']=OrderedDict(fields)
#R5
def write_get_or_create_title(model_dict,sheet,sheet_of_copy_wb,title_row,key_tram):
    fields = model_dict['fields']
#     print ('fields',fields)
    for fname,attr in fields.items():
#         childrend_model_dict =  attr
#         childrend_fields = attr.get('fields')
        if attr.get('fields'):
            write_get_or_create_title(attr,sheet,sheet_of_copy_wb,title_row,key_tram)
        offset_write_xl = get_key(attr, 'offset_write_xl')
        if offset_write_xl !=None:
            col =  sheet.ncols + offset_write_xl 
            title = attr.get('string',fname)  + u' sẵn hay tạo'
            sheet_of_copy_wb.col(col).width =  get_width(len(title))
            sheet_of_copy_wb.write(title_row, col,title ,header_bold_style)


def rut_gon_key(MD,key_tram,mode_no_create_in_main_instance=None): 
#         raise UserError(u'kkakaka 1')
    for attr,val in MD.items():
        if attr != 'fields':
#             if attr !='get_or_create_para':
            adict = TYPES_ATT_DICT.get(attr,{})
#             if adict == None:
#                 raise UserError(u'**None** attr:%s- attr_val:%s- thiếu attr trong TYPES_ATT_DICT'%(attr,val))
            default = adict.get('default')
            val = get_by_key_tram(MD, attr, key_tram,default)
            if attr =='skip_this_field' and mode_no_create_in_main_instance:
                skip_this_field_for_mode_no_create = get_by_key_tram(MD, 'skip_this_field_for_mode_no_create', key_tram)
                if skip_this_field_for_mode_no_create==True:
                    val = True
#             elif attr =='skip_this_field_for_mode_no_create':
#                 MD['skip_this_field'] = val
            MD[attr] = val
#         elif MD['fields'] :
        else :
            fields = MD['fields']
            if isinstance(fields, dict):
                fields = get_by_key_tram(MD, attr, key_tram,default)
                MD[attr] = fields
            if fields != None:
                print ('***fields',fields)
                for field_name, field_attr_is_MD_child in fields: 
                    rut_gon_key(field_attr_is_MD_child,key_tram,mode_no_create_in_main_instance=mode_no_create_in_main_instance)

#R3
def recursive_add_model_name_to_field_attr(self,MODEL_DICT,key_tram=False):
    model_name = get_key(MODEL_DICT, 'model')
    fields= self.env[model_name]._fields
    for f_name,field_attr in MODEL_DICT.get('fields').items():
        f_name = get_key(field_attr, 'transfer_name') or  f_name
        skip_this_field = get_key(field_attr, 'skip_this_field',False)
        if callable(skip_this_field):
            skip_this_field = skip_this_field(self)
        if not skip_this_field:
            if f_name not in fields and not field_attr.get('for_excel_readonly'):
                raise UserError(u'f_name:"%s" không nằm trong fields, phải thêm thược tính for_excel_readonly-field_attr:%s'%(f_name,field_attr))
            if not field_attr.get('for_excel_readonly') :# and not skip_this_field
                try:
                    field = fields[f_name]
                except:
                    raise UserError(u'field %s không có trong  danh sách fields của model %s'%(f_name,model_name))
                field_attr['field_type'] = field.type
                if field.comodel_name:
                    field_attr['model'] = field.comodel_name
                
                if 'required' not in field_attr:
                    required_from_model = field.required
                    required_force = field_attr.get('required_force',None)
    #                 bypass_this_field_if_value_equal_False = field_attr.get('bypass_this_field_if_value_equal_False')  # nó tự default là gì đó
    #                 if bypass_this_field_if_value_equal_False:
    #                     required = False
    #                 else:
                    if required_force:
                        required =True
                    else:
                        required = required_from_model
                    field_attr['required']= required
            if field_attr.get('fields'):
                    recursive_add_model_name_to_field_attr(self,field_attr,key_tram=key_tram)
                    
                    
                    

#R3
def check_set_val_is_true_type(val, attr):
#     if attr not in TYPES_ATT_DICT:
#         return False
#     else:
#         return True
    python_type_of_val = type(val)
    adict = TYPES_ATT_DICT.get(attr)
    set_types_of_manual_attr = adict.get('types')
    if  callable(val):
        string_type_of_val = 'function'
    elif val == None or adict.get('no_need_check_type'):
        return True
    else:
        string_type_of_val = STRING_TYPE_DICT.get(python_type_of_val,None)   
     
    if not adict:
        raise UserError(u'attr:%s chưa có liệt kê  trong TYPES_ATT_DICT'%attr)
    
    if string_type_of_val not in set_types_of_manual_attr:
        
        raise UserError (u'attr %s val %s, type:%s, không đúng dữ liệu %s'%(attr,val,string_type_of_val,set_types_of_manual_attr))
        return False
    else:
        return True
                    
def check_xem_att_co_nam_ngoai_khong(COPY_MODEL_DICT,key_tram):
    for attr,valg in COPY_MODEL_DICT.items():
        if attr != 'fields':
            val = COPY_MODEL_DICT.get(attr)
            if not check_set_val_is_true_type(val,attr):
                raise UserError (u'attr %s val %s không thỏa hàm check_set_val_is_true_type'%(attr,valg))
        elif attr =='fields' : 
            for field,field_attr in COPY_MODEL_DICT['fields'].items():
                for attr,valg in field_attr.items():
#                     if attr != 'fields' and attr !='get_or_create_para':
                    if attr != 'fields' and attr !='get_or_create_para':
                        val = field_attr.get(attr)
                        if not check_set_val_is_true_type(val,attr):
                            raise UserError (u'Thuộc tính nằm ngoài danh sách cho phép: attr %s val %s'%(attr,valg))
                if 'fields' in field_attr:
                    check_xem_att_co_nam_ngoai_khong(field_attr,key_tram)
                                    
    
        
        


# R4
def add_col_index(MODEL_DICT, read_excel_value_may_be_title, col,key_tram):
    
    is_map_xl_title = False
    for field,field_attr in MODEL_DICT.get('fields').items():
        is_real_xl_match_with_xl_excel = False
        xl_title = get_key(field_attr,'xl_title')
        if get_key(field_attr,'set_val') != None:
            continue
        if xl_title ==None and get_key(field_attr,'col_index') !=None:
            continue# cos col_index
        elif field_attr.get('fields'):
            is_real_xl_match_with_xl_excel = add_col_index(field_attr, read_excel_value_may_be_title, col,key_tram)
        elif xl_title:
            if isinstance(xl_title, list):
                xl_title_s = xl_title
            else:
                xl_title_s = [xl_title]
            for xl_title in xl_title_s:
                xl_title_partern = u'^%s$'%xl_title
#                 xl_title_partern = xl_title
#                 xl_title_partern = xl_title_partern.replace('/','//').replace('(','/(').replace(')','/)')
                xl_title_partern = xl_title_partern.replace('\\','\\\\').replace('(','\(').replace(')','\)')
                is_map = re.search(xl_title_partern,read_excel_value_may_be_title,re.IGNORECASE)
                is_map = is_map or (xl_title==read_excel_value_may_be_title)
                if is_map:
                    field_attr['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey
def define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram):
#     read_excel_value_may_be_titles = []
#     titles = []
    row_title_index =None
    number_map_dict = {}
    for row in title_rows:
        if row >= sheet.nrows:
            break
        for col in range(0,sheet.ncols):
            if VERSION_INFO ==2:
                read_excel_value_may_be_title = unicode(sheet.cell_value(row,col))
            else:
                read_excel_value_may_be_title = str(sheet.cell_value(row,col))
            is_map_xl_title = add_col_index( COPY_MODEL_DICT, read_excel_value_may_be_title, col,key_tram)
#             read_excel_value_may_be_titles.append(read_excel_value_may_be_title)
            if is_map_xl_title:
                row_title_index = row
#                 number_map_dict.setdefault(row,0)
                number_map_dict[row] =number_map_dict.get(row,0) + 1
#                 titles.append(read_excel_value_may_be_title)
#     print ('***number_map_dict',number_map_dict)
    if not number_map_dict:
        raise UserError(u'number_map_dict rỗng')
    largest_map_row = max(number_map_dict.items(), key=operator.itemgetter(1))[0]
    return row_title_index,largest_map_row



#R5
def check_col_index_match_xl_title_for_a_field(field_attr,xl_title,col_index,set_val,key_tram,needdata,field_name,func):
#         if field_attr.get('model'):
#             if (xl_title or col_index):
#                 raise UserError(u'có model thì không cần xl title')

        if xl_title and col_index==None and set_val==None :
            sheet_allow_this_field_not_has_exel_col =get_key( field_attr,'sheet_allow_this_field_not_has_exel_col')
            skip_field_if_not_found_column_in_some_sheet = get_key(field_attr,'skip_field_if_not_found_column_in_some_sheet')
            skip_if_not_match =  skip_field_if_not_found_column_in_some_sheet or (sheet_allow_this_field_not_has_exel_col and needdata['sheet_name'] in sheet_allow_this_field_not_has_exel_col)
            if not skip_if_not_match:
#                 raise UserError(u'có khai báo xl_title nhưng không match với file excel, field: %s, xl_title: %s -- attr%s' %(field_name,xl_title,field_attr))
                raise UserError(_(u'Excel not has column one in %s of %s, please change column name match with them') %(xl_title,field_name))
        if xl_title == None and col_index==None and set_val ==None:
            if  field_attr.get('model'):
                if not func and not field_attr.get('fields'):
                    raise UserError(u'model thì phải có ít nhất func và fields')
            else:
                if not func:
                    raise UserError (u' sao khong có col_index và  không có func luôn field %s attrs %s'%(field_name,u'%s'%field_attr))
                
                
def check_col_index_match_xl_title(self,COPY_MODEL_DICT,key_tram,needdata):
    for field_name,field_attr in COPY_MODEL_DICT.get('fields').items():
        skip_this_field = get_key(field_attr, 'skip_this_field', False)
        if callable(skip_this_field):
                skip_this_field = skip_this_field(self)
        if not skip_this_field: 
            col_index = get_key(field_attr, 'col_index', None)
            xl_title = get_key(field_attr, 'xl_title')#moi them , moi bo field_attr.get('xl_title')
            ###  deal set_val ########
            set_val = get_key( field_attr,'set_val')
            if callable(set_val):
                    set_val = set_val(self)
            field_attr['set_val'] =set_val
            func = get_key( field_attr,'func')
            check_col_index_match_xl_title_for_a_field(field_attr,xl_title,col_index,set_val,key_tram,needdata,field_name,func)
            child_fields =  field_attr.get('fields')
            if child_fields:
                check_col_index_match_xl_title(self,field_attr,key_tram,needdata)
    

                
                
#!5
#R4             
def muon_xuat_dac_tinh_gi(COPY_MODEL_DICT, attr_muon_xuats = ['field_type'],ghom_dac_tinh = {}):
    #ghom_dac_tinh = {'field_type':['char','many2one']}
    fields = COPY_MODEL_DICT['fields']
    some_att_fields = {}
    #some_att_fields = {
    for field,field_attr in fields.items():
        one_field_attrs = {}
        for attr_muon_xuat in attr_muon_xuats:
            if attr_muon_xuat in field_attr:
                val = field_attr.get(attr_muon_xuat)
                one_field_attrs[attr_muon_xuat] = val
                alist = ghom_dac_tinh.setdefault(attr_muon_xuat,[])
                if val not in alist:
                    alist.append(val)
        if 'fields' in field_attr:
            child_dict = muon_xuat_dac_tinh_gi(field_attr,attr_muon_xuats,ghom_dac_tinh)
            one_field_attrs['fields'] = child_dict
        some_att_fields[field] = one_field_attrs 
    return some_att_fields

def xuat_het_dac_tinh(COPY_MODEL_DICT,key_tram,dac_tinhs = {}):
    fields = COPY_MODEL_DICT['fields']
    for field,field_attr in fields.items():
        for attr,val in field_attr.items():
            a_dt_list = dac_tinhs.setdefault(attr,[])
            val = get_key(field_attr, attr)
            if val not in a_dt_list :
                a_dt_list.append(val)
        if 'fields' in field_attr:
            xuat_het_dac_tinh(field_attr,key_tram,dac_tinhs)


