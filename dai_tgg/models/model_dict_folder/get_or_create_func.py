 # -*- coding: utf-8 -*-
from odoo.addons.dai_tgg.models.model_dict_folder.tool_tao_instance import get_key
from odoo.osv import expression
import datetime
from odoo import  fields
from odoo.exceptions import UserError
def get_or_create_object_has_x2m (self, class_name, search_dict,
                                write_dict ={},
                                is_must_update=False, 
                                noti_dict=None,
                                inactive_include_search = False,
                                x2m_field=False,
                                remove_all_or_just_add_one_x2m = True,
#                                 is_return_get_or_create = True,
#                                  not_update_field_if_instance_exist_list=[],
#                                  dict_get_or_create_para_all_field={},
                                 model_dict = {},
                                 key_tram =  None,
#                                  only_search = False,
                                 exist_val=False,
#                                  search_func_para={},
                                 setting= {},
                                check_file = False,
                                is_search = True,
                                is_create = True,
                                is_write = True,
#                                 instance_some_dict={}
                                 ):
    
    if x2m_field:
        x2m_values = search_dict[x2m_field]
#         if not x2m_values:
#             return False,False,False
        result = []
        get_or_create = False
        for val in x2m_values:
            search_dict[x2m_field] = val #
            obj, get_or_create_iterator = get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,
#                                     ,is_return_get_or_create=True,
#                                     not_update_field_if_instance_exist_list=not_update_field_if_instance_exist_list,
#                                     dict_get_or_create_para_all_field = dict_get_or_create_para_all_field,
                                    model_dict = model_dict,
                                    key_tram = key_tram,
#                                     only_search = only_search,
                                    exist_val=exist_val,
#                                     search_func_para=search_func_para,
                                    setting = setting,
                                    check_file = check_file,
                                    is_search = is_search,
                                    is_create = is_create,
                                    is_write = is_write,
#                                     instance_some_dict=instance_some_dict
                                        
                                    )
            result.append(obj.id)
            get_or_create |=get_or_create_iterator
        if remove_all_or_just_add_one_x2m == True:
            obj_id =  [(6,False,result)]
        else:
            obj_id =  [(4,result[0],False)]
    else:
        obj, get_or_create =  get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,
                                    model_dict = model_dict,
                                    key_tram = key_tram,
#                                     only_search = only_search,
                                    exist_val=exist_val,
#                                     search_func_para=search_func_para,
                                    setting = setting,
                                    check_file = check_file,
                                    is_search = is_search,
                                    is_create = is_create,
                                    is_write = is_write,
#                                     instance_some_dict=instance_some_dict
                                    )
#         obj_id = obj.id
#         if obj :
#             if search_func_para.get('exist_val'):
#                 obj_id = True
#             else:
#                 obj_id = obj.id
#         else:
        if obj != None and  obj != False:
            obj_id = obj.id
        else:
            obj_id = obj
#     if is_return_get_or_create:
    return obj, obj_id, get_or_create



        

def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False,
                                model_dict = {},
                                key_tram = None,
#                                 only_search = False,
                                exist_val=False,
#                                 search_func_para={},
                                setting = {},
                                check_file=False,
                                is_search = True,
                                is_create = True,
                                is_write = True,
#                                 instance_some_dict={}
                                ):
    search_dict_new = {}
    write_dict_new = {}
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    
#     is_search = True
    
#     if only_search:
#         is_create = False
#         is_write = False
#         
#     else:
#         if exist_val:
#             is_create = False
#             is_write = True
#         else:
#             is_create = True
#             is_write = True
    
    if is_search:
        this_model_noti_dict['search'] = this_model_noti_dict.get('search',0) + 1
        search_func = model_dict.get('search_func')
        if search_func:
            searched_object = search_func(model_dict,self,exist_val,setting)
            if not searched_object and is_create:
                for f_name in search_dict:
                    field_attr = model_dict['fields'][f_name]
                    val =  search_dict[f_name]
                    f_name = get_key(field_attr, 'transfer_name') or f_name
                    search_dict_new[f_name] =  val
        else:
            if inactive_include_search:
                domain_not_active = ['|',('active','=',True),('active','=',False)]
            else:
                domain_not_active = []
            domain = []
            break_condition = False
            for f_name in search_dict:
                field_attr = model_dict['fields'][f_name]
                val =  search_dict[f_name]
#                 if only_search and val == None:
#                     return None,None
                if val == None:
                    if check_file:
                        searched_object,get_or_create =  None,False
                        break_condition = True
                        break
                    else:
                        raise UserError(u'val không thể bằng None')
                f_name = get_key(field_attr, 'transfer_name') or f_name
                operator_search = field_attr.get('operator_search','=')
                tuple_in = (f_name, operator_search, val)
                domain.append(tuple_in)
                if is_create:
                    search_dict_new[f_name] =  val
            
            if not break_condition:
                domain = expression.AND([domain_not_active, domain])
                searched_object  = self.env[class_name].search(domain)
            
        return_obj = searched_object 
        get_or_create = bool(searched_object)
        if get_or_create:
            this_model_noti_dict['search_yes'] = this_model_noti_dict.get('search_yes',0) + 1
        else:
            this_model_noti_dict['search_no'] = this_model_noti_dict.get('search_no',0) + 1
    else:
        return_obj = None 
        get_or_create = None
    if is_create:
        if not searched_object  :#create
            only_get = get_key(model_dict,'only_get')
            if only_get:
                raise UserError(u'Model %s này chỉ được get chứ không được tạo'%class_name)
            for f_name,val in write_dict.items():
                field_attr = model_dict['fields'][f_name]
                f_name = get_key(field_attr, 'transfer_name') or f_name
                search_dict_new[f_name]=val
            created_object = self.env[class_name].create(search_dict_new)
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
            return_obj =  created_object
            return return_obj,get_or_create
    allow_write_all_field = setting['allow_write']
    if is_write  :  
        if exist_val:
            searched_object = exist_val
        if searched_object :# write
            if len(searched_object) > 1:
                raise UserError (u' exist_val: %s len(searched_object) > 1, searched_object: %s'%(exist_val,searched_object))
            for f_name,val in write_dict.items():
                field_attr = model_dict['fields'][f_name]
                f_name = get_key(field_attr, 'transfer_name') or f_name

                if 'write_field' in field_attr and field_attr['write_field'] != None :
                    write_field = field_attr['write_field']
                else:
                    write_field = allow_write_all_field
                
                
#                 allow_write_from_False_to_not_false = field_attr.get('allow_write_from_False_to_not_false',True)   
                allow_write_from_False_to_not_false = field_attr.get('allow_write_from_False_to_not_false')   if 'allow_write_from_False_to_not_false' in field_attr else setting['allow_write_from_False_to_not_false']
                if allow_write_all_field and write_field == False and val ==False:
                    if  allow_write_from_False_to_not_false:
                        write_field = True
                print ('class_name',write_field)

               
                write_func = field_attr.get('write_func')
                if write_func:
                    code = write_func(searched_object=searched_object, f_name=f_name,val=val)
                    if code =='continue':
                        continue
                raise_if_diff = field_attr.get('raise_if_diff')
                if raise_if_diff:
                    if  val==False and allow_write_from_False_to_not_false: 
                        raise_if_diff = False
                    else:
                        raise_if_diff_only_write =  field_attr.get('raise_if_diff_only_write',True)
                        if raise_if_diff_only_write:
                            raise_if_diff = field_attr.get('raise_if_diff') and write_field
                            
                            
                if not (write_field or raise_if_diff) :
                    print ('field_name',f_name,'continue')
                    continue
                if not is_must_update or raise_if_diff :
                    orm_field_val = getattr(searched_object, f_name)
                    diff = check_diff_write_val_with_exist_obj(orm_field_val,val)
                    if diff:
                        if raise_if_diff:
                            raise UserError(u'raise_if_diff model:%s-f_name:%s - orm_field_val: %s -  val:%s '%(class_name,f_name,orm_field_val,val))
                        if write_field:
                            write_dict_new[f_name] = val
                        
                else:
                    write_dict_new[f_name] = val
            
            if write_dict_new:
                if model_dict.get('print_write_dict_new',False):
                    print ('***write_dict_new***',write_dict_new)
                searched_object.write(write_dict_new)
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
            else:#'not update'
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        
    return return_obj, get_or_create# bool(searched_object)

def check_diff_write_val_with_exist_obj(orm_field_val,field_dict_val):
    is_write = False
    try:
        converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
        if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder set = ()
            converted_orm_val_to_dict_val = False
    except:
        converted_orm_val_to_dict_val = orm_field_val
    if isinstance(orm_field_val, datetime.date):
        converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
    if converted_orm_val_to_dict_val != field_dict_val:
        is_write = True
    return is_write
    
                
                

