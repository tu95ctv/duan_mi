
# -*- coding: utf-8 -*-
import pytz
from odoo import models, fields, api,exceptions,tools,_
import re
from unidecode import unidecode
import sys
import datetime
from odoo.osv import expression

def pn_replace(pn):
    if pn:
        pn_replace =  re.sub('[- _ \s \\\ \/ |.]','',pn)
        return pn_replace
    else:
        pn_replace = pn
    return pn_replace
    
def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False):
    
    
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    else:
        this_model_noti_dict = None
    if inactive_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(write_dict)
        #print '***search_dict***',search_dict
        created_object = self.env[class_name].create(search_dict)
        if this_model_noti_dict !=None:
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
        return_obj =  created_object
    else:
        if not is_must_update:
            is_write = False
            for f_name in write_dict:
                field_dict_val = write_dict[f_name]
                orm_field_val = getattr(searched_object, f_name)
                try:
                    converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
                    if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder sset = ()
                        converted_orm_val_to_dict_val = False
                except:#not singelton
                    pass
                if isinstance(orm_field_val, datetime.date):
                    converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
                if converted_orm_val_to_dict_val != field_dict_val:
                    is_write = True
                    break
        else:
            is_write = True
        if is_write:
            searched_object.write(write_dict)
            if this_model_noti_dict !=None:
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
        else:#'not update'
            if this_model_noti_dict !=None:
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        return_obj = searched_object
    return return_obj



def convert_float_to_ghi_chu_ngay_xuat(val):
    if isinstance(val, float):
        seconds = (val - 25569) * 86400.0
        try:
            val= datetime.datetime.utcfromtimestamp(seconds).strftime('%d/%m/%Y')
        except ValueError:# year is out of range
            pass
    return val 
VERSION_INFO   = sys.version_info[0]
if VERSION_INFO ==2:
    unicode =  unicode
else:
    unicode  =  str

def viet_tat(string):
    string = string.strip()
    ns = re.sub('\s{2,}', ' ', string)
    ns = re.sub('[^\w ]','', ns,flags = re.UNICODE)
    slit_name = ns.split(' ')
    slit_name = filter(lambda w : True if w else False, slit_name)
    one_char_slit_name = map(lambda w: w[0],slit_name)
    rs = ''.join(one_char_slit_name).upper()
    return rs
def name_khong_dau_compute(self_):
    for r  in self_:
        if r.name:
            name = r.name
            if name:
                try:
                    name_khong_dau = unidecode(name)
                except:
                    raise ValueError(name)
                r.name_khong_dau = name_khong_dau
                r.name_viet_tat = viet_tat(name_khong_dau)
def convert_utc_to_gmt_7(utc_datetime_inputs):
    local = pytz.timezone('Etc/GMT-7')
    utc_tz =pytz.utc
    gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
    gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
    gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
    return gio_bat_dau_vn
def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        return vn_time
  
def convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn):
            local = pytz.timezone('Etc/GMT-7')
            utc_tz =pytz.utc
            gio_bat_dau_in_vn = local.localize(native_ca_gio_in_vn, is_dst=None)
            gio_bat_dau_in_utc = gio_bat_dau_in_vn.astimezone (utc_tz)
            return gio_bat_dau_in_utc
        
def convert_odoo_datetime_to_vn_str(odoo_datetime, format='%d/%m/%Y %H:%M' ):
    if odoo_datetime:
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        vn_time_str = vn_time.strftime(format)
        return vn_time_str
    else:
        return False
def convert_memebers_to_str(member_ids):
    return u','.join(member_ids.mapped('name'))

def Convert_date_orm_to_str(date_orm_str,format_date = '%d/%m/%y'):
    if date_orm_str:
        date_obj = fields.Date.from_string(date_orm_str)
        return date_obj.strftime(format_date)
    else:
        return False
    
def convert_date_odoo_to_str_vn_date(odoo_date):
    return Convert_date_orm_to_str(odoo_date,format_date = '%d/%m/%Y')
    
    
    
    
# adict=[
#                                                                 ('code',{}),
#                                                                 ('name',{'func': lambda x:name}),
#                                                                 ('diem',{'pr':u'Điểm'}),
#                                                                 ('don_vi',{'pr':u'Đơn Vị','func':lambda r: r.name}),
#                                                                ]

def name_compute(r,adict=None,join_char = u' - ',junc_char=u':'):
    names = []
    for fname,attr_dict in adict:
#         not_use_val = attr_dict.get('attr_dict')
        val = getattr(r,fname)
        func = attr_dict.get('func',None)
        karg = attr_dict.get('karg',{})
        
        if func:
            val = func(val,**karg)
        else:
            if hasattr(val, 'name'):
                val = val.name
        if  val ==False or (not val and  fname=='id' ):# Cho có trường hợp New ID
            if attr_dict.get('skip_if_False',True):
                continue
            if  fname=='id' :
                val ='New'
            else:
                val ='_'
        if attr_dict.get('pr',None):
            a_junc_char = attr_dict.get('junc_char',junc_char)
            item =  attr_dict['pr'] + a_junc_char + ' ' + unicode(val)
        else:
            item = unicode (val)
        names.append(item)
    if names:
        name = join_char.join(names)
    else:
        name = False
    return name







# def name_compute_char_join_rieng(r,adict=None,join_char = u' - '):
#     names = []
# #     adict = [('cate_cvi',{'pr':''}),('noi_dung',{'pr':'','func':lambda r: r.name }),('id',{'pr':''})]
#     sum_txt = ''
#     for c,fname_and_attr_dict in enumerate(adict):
#         fname,attr_dict = fname_and_attr_dict
#         val = getattr(r,fname)
#         func = attr_dict.get('func',None)
#         pr_more = attr_dict.get('pr_more','')
#         sf_more = attr_dict.get('sf_more','')
#         join_char_of_one_field = attr_dict.get('join_char',join_char)
#         if func:
#             val = func(val)
#         if  not val:# Cho có trường hợp New ID
#             if attr_dict.get('skip_if_False',True) and  (pr_more=='' and sf_more==''):
#                 continue
#             if  fname=='id' :
#                 val ='New'
#             else:
#                 val ='_'
#         if attr_dict.get('pr') != None:
#             item =  attr_dict['pr'] + u': ' + unicode(val)
#         else:
#             item = unicode (val)
#             
#         if pr_more:
#             item =  pr_more +  val
#         if sf_more:
#             item =  val + sf_more
#         if c ==0:
#             pass
#         else:
#             item =join_char_of_one_field + item
#         sum_txt = sum_txt + item
# #         names.append(item)
# #     if names:
# #         name = join_char.join(names)
# #     else:
# #         name = False
#     if sum_txt:
#         pass
#     else:
#         sum_txt = False
#     return sum_txt



    
# def Convert_datetime_orm_to_str(date_orm_str):
#     if date_orm_str:
#         date_obj = fields.Datetime.from_string(date_orm_str)
#         return date_obj.strftime('%d/%m/%y %H:%M')
#     else:
#         return False
    
    
# def convert_utc_to_gmt_7(utc_datetime_inputs):
#     local = pytz.timezone('Etc/GMT-7')
#     utc_tz =pytz.utc
#     gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
#     gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
#     gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
#     return gio_bat_dau_vn
# def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
#         utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
#         vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
#         return vn_time
#   
# def convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn):
#             local = pytz.timezone('Etc/GMT-7')
#             utc_tz =pytz.utc
#             gio_bat_dau_in_vn = local.localize(native_ca_gio_in_vn, is_dst=None)
#             gio_bat_dau_in_utc = gio_bat_dau_in_vn.astimezone (utc_tz)
#             return gio_bat_dau_in_utc
#         
# def convert_odoo_datetime_to_vn_str(odoo_datetime):
#     if odoo_datetime:
#         utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
#         vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
#         vn_time_str = vn_time.strftime('%d/%m/%Y %H:%M')
#         return vn_time_str
#     else:
#         return False
#     
    
    