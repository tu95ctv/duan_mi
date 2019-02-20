# -*- coding: utf-8 -*-
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo.exceptions import UserError
from copy import deepcopy
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict
from odoo.addons.dai_tgg.mytools import  Convert_date_orm_to_str
from collections import  OrderedDict
from odoo.addons.downloadwizard.models.dl_models.dl_model import  write_all_row,generate_easyxf
# from odoo.addons.downloadwizard.models.dl_models.dl_model import  get_width
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_
from odoo.addons.downloadwizard.models.dl_models.dl_model import  bold_style,normal_style
from dateutil.relativedelta import relativedelta

from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date, convert_utc_to_gmt_7
import datetime


def gen_domain_cvi_date(dl_obj,theo_sql = False):
    if not theo_sql:
        domain = [('loai_record','=',u'Công Việc')]
    else:
        where_clause_list = []
    if dl_obj.chon_thang ==u'Tháng Này':
        utc_time = datetime.datetime.now()
        vn_time = convert_utc_to_gmt_7(utc_time)
        vn_thang_nay_date_begin = vn_time.strftime('%Y-%m-01')
        vn_time_offset_thang_sau =  vn_time + relativedelta(months=1)
        vn_thang_nay_date_end = vn_time_offset_thang_sau.strftime('%Y-%m-01')
        if not theo_sql:
            domain.extend([('ngay_bat_dau','>=',vn_thang_nay_date_begin),('ngay_bat_dau','<',vn_thang_nay_date_end)])
        else:
            where_clause_list.append('cvi.ngay_bat_dau >= %s'%vn_thang_nay_date_begin)
            where_clause_list.append('cvi.ngay_bat_dau < %s'%vn_thang_nay_date_end)
    elif dl_obj.chon_thang ==u'Tháng Trước':
        utc_time = datetime.datetime.now()
        vn_time = convert_utc_to_gmt_7(utc_time)
        thang_truoc_time = vn_time + relativedelta(months=-1)
        thang_truoc_date_begin = thang_truoc_time.strftime('%Y-%m-01')
        thang_truoc_date_end = vn_time.strftime('%Y-%m-01')
        if not theo_sql:
            domain.extend([('ngay_bat_dau','>=',thang_truoc_date_begin),('ngay_bat_dau','<',thang_truoc_date_end)])
        else:
            where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%thang_truoc_date_begin)
            where_clause_list.append("cvi.ngay_bat_dau < '%s'"%thang_truoc_date_end)
    else:
        if dl_obj.date:
            if not theo_sql:
                domain.append(('ngay_bat_dau','>=',dl_obj.date))
            else:
                where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%dl_obj.date)
        if dl_obj.end_date:
            if not theo_sql:
                domain.append(('ngay_bat_dau','<=',dl_obj.end_date))
            else:
                where_clause_list.append("cvi.ngay_bat_dau <= '%s'"%dl_obj.end_date)
    if not theo_sql:
        return domain
    else:
        return where_clause_list



FIELDNAME_FIELDATTR_cvi =OrderedDict( [
        ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
        ('ngay_bat_dau',{'func': lambda v,n: Convert_date_orm_to_str(v),'width':10}),
        ('gio_bat_dau',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
        ('gio_ket_thuc',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
        ('code',{}),
        ('tvcv_id_name',{}),
        ('noi_dung',{}),
        ('slncl',{}),
         ('cd_children_ids',{'func':lambda val,n: ','.join(map(lambda v:u'%s'%v.login ,val.mapped('user_id')))}),
         ('diem_tvi',{}),
         ('so_luong',{}),
         ('so_lan',{}),
         ('slncl',{}),
         ('ti_le_chia_diem',{}),
         ('diemtc',{}),
         ('diemld',{}),    
                    ]
                                     
                                     )

Export_Para_cvi = {
    'exported_model':'cvi',
#     'max_char_width':50,
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_cvi,
    'gen_domain':gen_domain_cvi_date,
    'search_para':{'order': 'loai_record asc'},#desc
    }





def dl_p3_per_user(dl_obj,user_id,wb = None,tram=None):
    font_height =dl_obj.font_height
    bold_style = xlwt.easyxf(generate_easyxf(height=font_height,bold=True))
    center_style = xlwt.easyxf(generate_easyxf(height=font_height,vert = 'center',horiz='center'))
    def sum_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
        begin_row = needdata['instance_dict']['table']['begin_row'] +2
        end_row = needdata['instance_dict']['table']['end_row']
        if end_row > begin_row:
            worksheet.write(row_index, 4, xlwt.Formula('SUM(%s%s:%s%s)'%('P',begin_row + 1,'P',end_row+1)),center_style)
        return 1# 1 row
    def table_detail_p3_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
        Export_Para_cvi_copy = deepcopy(Export_Para_cvi)
        n_row = download_model(dl_obj,
                     Export_Para=Export_Para_cvi_copy,
                     append_domain=kargs['append_domain_user_id'],
                     workbook=None,
                     worksheet=worksheet,
                     ROW_TITLE = row_index + 1,
                     return_more_thing_for_bcn = True,
                     no_gray = True,
                     OFFSET_COLUMN = 1,
                                                   
                 )
        return n_row

    fixups =[  
                 ('trung_tam1',{'range':[0,0,0,3],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=11, vert = 'center',horiz = 'center'))}),
                 ('trung_tam2',{'range':[1,1,0,3],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('diem_tong_nhan_vien_cham_title',{'range':[5, 3],'val':u'Điểm Tổng Nhân Viên Chấm'}),
                 ('ho_ten_title',{'range':[3, 3],'val':u'Họ Tên','style':bold_style}),
                 ('ho_ten',{'range':[3, 4],'val':user_id.name}),
                 ('tram_tilte',{'range':[4, 3],'val':u'Trạm'}),
                 ('tram',{'range':[4, 4],'val':tram,'style':bold_style}),
                 ('table',{'range':[9, 0],'val':None,'func':table_detail_p3_ ,'offset':3 ,'kargs':{'append_domain_user_id':[('user_id','=',user_id.id)]}}),
                 ('sum',{'range':[5, 4],'func':sum_ })
                 ]
    wb = write_all_row(fixups,dl_obj,None,wb = wb,ws_name=user_id.name,font_height=font_height )
    return wb
def gen_department_id(dl_obj):
    if dl_obj.department_id:
        if dl_obj.user_has_groups('base.group_erp_manager'):
            dp_id = dl_obj.department_id
        else:
            dp_id = dl_obj.env.user.department_id
    else:
            dp_id = dl_obj.env.user.department_id
    return dp_id
def dl_p3(dl_obj,append_domain = []):
    department_id =gen_department_id(dl_obj)
    cates = dl_obj.env['res.users'].search([('department_id','=',department_id.id)])
    wb = None
    if dl_obj.chi_tiet_hay_danh_sach =='danh_sach':
        filename = u'p3_ds_%s'%department_id.name
        wb = download_cvi_by_userlist(dl_obj)
    else:
        filename = u'p3_user_%s'%department_id.name
        for user_id in cates:
            wb = dl_p3_per_user(dl_obj,user_id,wb, department_id.name)
    name = "%s%s" % (filename, '.xls')
    return wb,name

def gen_date_and_department_domain(dl_obj):
    domain = []
    dp_id =gen_department_id(dl_obj)
    domain = [('department_id','=',dp_id.id)]
    domain_date = gen_domain_cvi_date(dl_obj)
    domain.extend(domain_date)
    return domain
def gen_read_group_domain_user_in_department(dl_obj):
    domain = gen_date_and_department_domain(dl_obj)
    read_group_rsul = dl_obj.env['cvi'].read_group(domain, ['user_id', 'diemtc', 'diemld'], ['user_id'], orderby='id')
    return read_group_rsul

def download_cvi_by_userlist(dl_obj):
    read_group_rsul = gen_read_group_domain_user_in_department(dl_obj)
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet 1')
    normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
    worksheet.write(0,0,'STT',normal_style)
    worksheet.write(0,1,u'Tên',normal_style)
    worksheet.write(0,2,u'Điểm', normal_style)
    row_index = 1
    stt =1
    for rs in read_group_rsul:
        worksheet.write(row_index,0,stt,normal_style)
        worksheet.write(row_index,1,str(rs['user_id'][1]),normal_style)
        worksheet.write(row_index,2,rs['diemtc'],normal_style)
        row_index += 1
        stt +=1
    return workbook




