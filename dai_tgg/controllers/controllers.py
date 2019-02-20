# -*- coding: utf-8 -*-
from odoo import http
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
# from openpyxl import load_workbook
# from cStringIO import StringIO
from odoo.tools.misc import xlwt
from copy import deepcopy
from odoo import api,fields
import datetime
import odoo.addons.web.controllers.pivot as pivot
import json
from odoo.tools import ustr
from collections import deque
# from tools import convert_odoo_datetime_to_vn_str
from odoo.osv import expression
from dateutil.relativedelta import relativedelta

import pytz
import string
from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date, convert_utc_to_gmt_7
from unidecode import unidecode

from odoo.addons.dai_tgg.models.dl_models.dl_tvcv import  download_tvcv
from odoo.addons.dai_tgg.models.dl_models.dl_user import  download_user
from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_bcn
from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_cvi
from odoo.addons.dai_tgg.models.dl_models.dl_p3 import  dl_p3


from odoo.addons.downloadwizard.download_tool import  download_all_model_by_url

# def FIELDNAME_FIELDATTR_flat(FIELDNAME_FIELDATTR,item_seperate=';',k_v_separate = ':'):
#     alist = []
#     for k,v in FIELDNAME_FIELDATTR.iteritems():
#         if isinstance(v,dict):
#             v = FIELDNAME_FIELDATTR_flat(v,item_seperate=',',k_v_separate = ' ')
#         alist.append(k + k_v_separate + v)
#     return item_seperate.join(alist)     

def get_width(num_characters):
    return int((1+num_characters) * 256)

def add_header_TrungTamHaTangMang(worksheet,user_id,ROW_TRUNG_TAM,offset_column,normal_style,bold_style,ROW_SUM,KEY_COL,VAL_COL):
    cty_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 256; align: horiz left, vert centre, wrap 1; alignment: wrap 1")# align: horiz centre, vert centre
    ROW_HO_TEN = ROW_TRUNG_TAM+ 1
    ROW_TRAM = ROW_TRUNG_TAM + 2
    
    worksheet.write_merge(ROW_TRUNG_TAM, ROW_TRUNG_TAM, 0, 4, u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM\n ĐÀI VIỄN THÔNG HỒ CHÍ MINH',cty_bold_style)
    worksheet.row(ROW_TRUNG_TAM).height_mismatch = True
    worksheet.row(ROW_TRUNG_TAM).height = 256*5
    worksheet.write(ROW_HO_TEN,KEY_COL,u'Họ và Tên',normal_style)
    worksheet.write(ROW_HO_TEN, VAL_COL,user_id.name,bold_style)
    worksheet.write(ROW_TRAM,KEY_COL, u'Trạm',normal_style)
    worksheet.write(ROW_TRAM,VAL_COL ,user_id.department_id.name,bold_style)
    worksheet.write(ROW_SUM, KEY_COL,u'Điểm Tổng LĐ Chấm',normal_style)
    worksheet.write(ROW_SUM, KEY_COL,u'Điểm Tổng Nhân Viên Chấm',normal_style)
    
def add_title(FIELDNAME_FIELDATTR,cvi_fields,offset_column,worksheet,ROW_TITLE):
    header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
    for title_column_index, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
                title_column_index += offset_column
                f_name, FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
                is_not_model_field = FIELDATTR.get('is_not_model_field')
                if is_not_model_field:
                    f_string =FIELDATTR.get('string') or  f_name
                else:
                    field = cvi_fields[f_name]
                    f_string = field.string
                worksheet.write(ROW_TITLE, title_column_index, f_string, header_bold_style)
                width  = FIELDATTR.get('width')
                if not width :
                    width = get_width(len(f_string))
                worksheet.col(title_column_index).width = width
def add_1_cvi_for_1_person(worksheet,FIELDNAME_FIELDATTR, r,offset_column,stt,row_index,normal_border_style):
    for title_column_index, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
        title_column_index += offset_column
        f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        if is_not_model_field:
            if f_name=='stt':
                val = stt
        else:
            val = getattr(r, f_name)
            func = FIELDATTR.get('func',None)
            if func:
                val = func(val)
            if val == False:
                val = u''
        worksheet.write(row_index, title_column_index, val, normal_border_style)    
def add_sum_info(worksheet,FIELDNAME_FIELDATTR,offset_column,num2alpha,ROW_TITLE,ROW_SUM,VAL_COL,last_row_index):
    for title_column_index, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
        title_column_index += offset_column
        f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        if FIELDATTR.get('is_not_model_field'):
            pass
        else:
            if FIELDATTR.get('sum'):
                intRowSum = FIELDATTR.get('row_sum')
                intColSum = FIELDATTR.get('col_sum')
                column_index_apha = num2alpha[title_column_index]
#                 worksheet.write(ROW_TITLE, title_column_index, xlwt.Formula('SUM(%s%s:%s%s)'%(column_index_apha,ROW_TITLE + 2,column_index_apha,row_index)))
                worksheet.write(intRowSum, intColSum, xlwt.Formula('SUM(%s%s:%s%s)'%(column_index_apha,ROW_TITLE + 2,column_index_apha,last_row_index)))

def filter_department_ids(department_ids):
    if department_ids:
        export_department_ids = department_ids.ids
    else:
        export_department_ids = [request.env.user.department_id.id]
    return export_department_ids


def generate_domain_date_and_department(dlcv_obj, theo_sql = False):
    domain = []
    if theo_sql == True:
        where_clause_list = []
        department_ids = dlcv_obj.department_ids
        export_department_ids = filter_department_ids(department_ids)
        if export_department_ids:
            if theo_sql:
                department_clause = ("cvi.department_id in %s"%(tuple(export_department_ids),)).replace(',)',')')
                where_clause_list.append(department_clause)
            else:
                domain.append(('department_id','in',export_department_ids))
        else:
            raise ValueError(u'Bạn không có quyền xem Báo cáo của những trạm đó')
    if dlcv_obj.chon_thang ==u'Tháng Này':
                utc_time = datetime.datetime.now()
                vn_time = convert_utc_to_gmt_7(utc_time)
                vn_thang_nay_date_begin = vn_time.strftime('%Y-%m-01')
                vn_time_offset_thang_sau =  vn_time + relativedelta(months=1)
                vn_thang_nay_date_end = vn_time_offset_thang_sau.strftime('%Y-%m-01')
                if theo_sql == False:
                    domain = expression.AND([[('ngay_bat_dau','>=',vn_thang_nay_date_begin),('ngay_bat_dau','<',vn_thang_nay_date_end)],domain])
                else:
                    where_clause_list.append('cvi.ngay_bat_dau >= %s'%vn_thang_nay_date_begin)
                    where_clause_list.append('cvi.ngay_bat_dau < %s'%vn_thang_nay_date_end)
    elif dlcv_obj.chon_thang ==u'Tháng Trước':
        utc_time = datetime.datetime.now()
        vn_time = convert_utc_to_gmt_7(utc_time)
        thang_truoc_time = vn_time + relativedelta(months=-1)
        thang_truoc_date_begin = thang_truoc_time.strftime('%Y-%m-01')
        thang_truoc_date_end = vn_time.strftime('%Y-%m-01')
        if theo_sql == False:
            domain = expression.AND([[('ngay_bat_dau','>=',thang_truoc_date_begin),('ngay_bat_dau','<',thang_truoc_date_end)],domain])
        else:
            where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%thang_truoc_date_begin)
            where_clause_list.append("cvi.ngay_bat_dau < '%s'"%thang_truoc_date_end)
    else:
        if dlcv_obj.ngay_bat_dau_filter:
            if theo_sql == False:
                domain = expression.AND([[('ngay_bat_dau','>=',dlcv_obj.ngay_bat_dau_filter)],domain])
            else:
                where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%dlcv_obj.ngay_bat_dau_filter)
            
        if dlcv_obj.ngay_ket_thuc_filter:
            if theo_sql == False:
                domain = expression.AND([[('ngay_bat_dau','<=',dlcv_obj.ngay_ket_thuc_filter)],domain])
            else:
                where_clause_list.append("cvi.ngay_bat_dau <= '%s'"%dlcv_obj.ngay_ket_thuc_filter)
        
    if theo_sql:
            where_clause = '  and '.join (where_clause_list)
            return  where_clause
    else:
        return domain



def download_cvi(dlcv_obj):
    num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
    normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
    normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;borders: left thin,right thin, top thin, bottom thin")
    bold_style = xlwt.easyxf("font: bold on")
    department_ids = dlcv_obj.department_ids
    export_department_ids = filter_department_ids(department_ids)
    user_ids = request.env['res.users'].search([('department_id','in',export_department_ids)])
    workbook = xlwt.Workbook()
    
    offset_column = 0
    ROW_TRUNG_TAM=0
    ROW_SUM = ROW_TRUNG_TAM + 3
    KEY_COL = offset_column + 3
    VAL_COL = offset_column + 4
    ROW_TITLE = ROW_TRUNG_TAM + 5
    
    FIELDNAME_FIELDATTR = [
             ('stt',{'is_not_model_field':True,'string':u'STT'}),
             ('ngay_bat_dau',{'func':convert_date_odoo_to_str_vn_date,'width':get_width(10)}),
             ('code',{}),('tvcv_id_name',{'width':get_width(40)}),('noi_dung',{'width':get_width(40)}),
             ('diem_tvi',{}),('so_luong',{}),('so_lan',{}),
             ('diemtc',{'sum':True, 'row_sum':ROW_SUM+1,  'col_sum':VAL_COL}),
             ('diemld',{'sum':True,'row_sum':ROW_SUM, 'col_sum':VAL_COL}),
                        ]
    domain = []
    domain_date = generate_domain_date_and_department(dlcv_obj)
    for user_id in user_ids:
        domain_user = [('user_id','=',user_id.id),('loai_record','=',u'Công Việc')]
        domain = expression.AND([domain_user, domain_date])
        worksheet = workbook.add_sheet(user_id.name,cell_overwrite_ok=True)
        add_header_TrungTamHaTangMang(worksheet,user_id,ROW_TRUNG_TAM,offset_column,normal_style,bold_style,ROW_SUM,KEY_COL,VAL_COL)
        cvi_fields = request.env['cvi']._fields
        add_title(FIELDNAME_FIELDATTR, cvi_fields, offset_column, worksheet, ROW_TITLE)
        row_index = ROW_TITLE + 1
        stt = 1
        person_records = request.env['cvi'].search(domain,order='ngay_bat_dau')
        for r in person_records:#request.env['cvi'].search([]):
            add_1_cvi_for_1_person(worksheet,FIELDNAME_FIELDATTR, r,offset_column, stt, row_index, normal_border_style)
            row_index +=1
            stt +=  1
        add_sum_info(worksheet,FIELDNAME_FIELDATTR,offset_column,num2alpha,ROW_TITLE,ROW_SUM,VAL_COL,row_index)
    return workbook
            
class DownloadCvi(http.Controller):
    @http.route('/web/binary/download_cvi_by_userlist',type='http', auth="public")
    def download_cvi_by_userlist(self,model, id, **kw):
        dlcv_obj = request.env[model].browse(int(id))
        where_clause = generate_domain_date_and_department (dlcv_obj, theo_sql = True)
        sql_cmd = '''select cvi.user_id,sum(diemtc),u.login,p.name from cvi inner join res_users as u on cvi.user_id = u.id inner join res_partner as p on u.partner_id = p.id %s group by cvi.user_id ,u.login,p.name'''
        sql_cmd = sql_cmd%((' where ' + where_clause )if where_clause else '')
        request.env.cr.execute(sql_cmd)
        rsul = request.env.cr.fetchall()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
        worksheet.write(0,0,'STT',normal_style)
        worksheet.write(0,1,u'Tên',normal_style)
        worksheet.write(0,2,u'Điểm', normal_style)
        row_index = 1
        stt =1
        for u_id,diem,login,name in rsul:
            worksheet.write(row_index,0,stt,normal_style)
            worksheet.write(row_index,1,login,normal_style)
            worksheet.write(row_index,2,diem,normal_style)
            row_index += 1
            stt +=1
            
            
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=table_cv_%s_%s.xls;'%(request.env.user.name, datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    @http.route('/web/binary/download_cvi',type='http', auth="public")
    def download_cvi(self,model, id, **kw):
        dlcv_obj = request.env[model].browse(int(id))
        workbook = download_cvi(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=chi_tiet_p3_%s_%s.xls;target=blank' %(unidecode(dlcv_obj.department_ids.name).replace(' ','_'), datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    
    
    @http.route('/web/binary/download_model',type='http', auth="public")
    def download_all_model_controller(self,**kw):
        response = download_all_model_by_url(kw)
        return response
    


        
    

        

        
