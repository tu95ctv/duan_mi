# -*- coding: utf-8 -*-
from odoo import models, fields, api
from time import sleep
import sys
VERSION_INFO   = sys.version_info[0]
try:
    import urllib.request as url_lib
except:
    import urllib2 as url_lib
# from odoo import fields
# from odoo.osv import expression
import datetime
# from unidecode import unidecode
from odoo.osv import expression
from odoo.exceptions import UserError


def get_key(field_attr, attr,default_if_not_attr=None):
    return field_attr.get(attr,default_if_not_attr)
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


def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False,
                                noti_dict={},
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
                                searched_object = False
#                                 instance_some_dict={}
                                ):
    search_dict_new = {}
    write_dict_new = {}
#     if noti_dict !=None:
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
                    try:
                        field_attr = model_dict['fields'][f_name]
                    except:
                        field_attr = {}
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
                try:
                    field_attr = model_dict['fields'][f_name]
                except:
                    field_attr = {}
                val =  search_dict[f_name]
#                 if only_search and val == None:
#                     return None,None
                if val == None:
                    if check_file:
                        searched_object, get_or_create =  None,False
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
                try:
                    field_attr = model_dict['fields'][f_name]
                except:
                    field_attr = {}
                f_name = get_key(field_attr, 'transfer_name') or f_name
                search_dict_new[f_name]=val
            created_object = self.env[class_name].create(search_dict_new)
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
            return_obj =  created_object
            return return_obj
    allow_write_all_field = setting.get('allow_write',True)
    if is_write  :  
        if exist_val:
            searched_object = exist_val
        if searched_object :# write
            if len(searched_object) > 1:
                raise ValueError (u' exist_val: %s len(searched_object) > 1, searched_object: %s, %s'%(exist_val,searched_object, searched_object.mapped('id')))
            for f_name,val in write_dict.items():
                try:
                    field_attr = model_dict['fields'][f_name]
                except:
                    field_attr = {}
                f_name = get_key(field_attr, 'transfer_name') or f_name

                if 'write_field' in field_attr and field_attr['write_field'] != None :
                    write_field = field_attr['write_field']
                else:
                    write_field = allow_write_all_field
                
                
#                 allow_write_from_False_to_not_false = field_attr.get('allow_write_from_False_to_not_false',True)   
                allow_write_from_False_to_not_false = field_attr.get('allow_write_from_False_to_not_false')   if 'allow_write_from_False_to_not_false' in field_attr else setting.get('allow_write_from_False_to_not_false',True)
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
                    orm_field_val = getattr(searched_object, f_name,None)
                    if orm_field_val ==None:
                        continue
                    diff = check_diff_write_val_with_exist_obj(orm_field_val,val)
                    if diff:
                        if raise_if_diff:
                            raise UserError(u'raise_if_diff model:%s-f_name:%s - orm_field_val: %s -  val:%s '%(class_name,f_name,orm_field_val,val))
                        if write_field:
                            write_dict_new[f_name] = val
                        
                else:
                    write_dict_new[f_name] = val
            
            if write_dict_new:
                if model_dict.get('print_write_dict_new',True):
                    print ('***write_dict_new***',write_dict_new)
                searched_object.write(write_dict_new)
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
            else:#'not update'
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        
    return return_obj# bool(searched_object)
class GethtmlError(Exception):
    pass

def request_html(url):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36' }
    count_fail = 0
    while 1:
        print ('dang get url: %s'%url)
        try:
            if VERSION_INFO == 3:
                req = url_lib.Request(url, None, headers)
                rp= url_lib.urlopen(req)
                mybytes = rp.read()
                html = mybytes.decode("utf8")
            elif VERSION_INFO ==2:
                req = url_lib.Request(url, None, headers)
                html = url_lib.urlopen(req).read()
            print ('da get %s'%url)

            return html
        except Exception as e:
            count_fail +=1
            sleep(5)
            if count_fail ==5:
                raise GethtmlError(u'%s'%url)
            