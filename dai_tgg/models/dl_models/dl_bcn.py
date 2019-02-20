# -*- coding: utf-8 -*-
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo import fields
from odoo.exceptions import UserError
from copy import deepcopy
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict
from odoo.addons.dai_tgg.mytools import  Convert_date_orm_to_str
from collections import  OrderedDict
from odoo.addons.downloadwizard.models.dl_models.dl_model import  write_all_row
from odoo.addons.downloadwizard.models.dl_models.dl_model import  get_width
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_
from odoo.addons.downloadwizard.models.dl_models.dl_model import  generate_easyxf,center_border_style
from odoo.addons.downloadwizard.models.dl_models.dl_model import  bold_style,bold_italic_style,normal_style,center_style,bold_center_18_style,bold_center_style


FIELDNAME_FIELDATTR_thuebao = [
          ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('msc',{}),
          ('date',{'func': lambda v,n: Convert_date_orm_to_str(v) }),
          ('tb_cap_nhat',{}),
          ('tb_mo_may',{}),
          ('tb_tat_may',{}),
          ('tai_cp',{}),
                    ]
Export_Para_thuebao = {
    'exported_model':'dai_tgg.thuebaoline',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_thuebao,
#     'gen_domain':gen_domain_stock_quant,
#     'search_para':{'order': 'loai_record asc'},#desc
    }
##################
def gen_domain_cvi(dl_obj):
    domain = []
    if dl_obj.date:
        domain.append(('ngay_bat_dau','>=',dl_obj.date))
    if dl_obj.end_date:
        domain.append(('ngay_bat_dau','<=',dl_obj.end_date))
        
    return domain
def generate_Export_Para_cvi(dl_obj):
    font_height =dl_obj.font_height
    center_border_style = xlwt.easyxf(generate_easyxf(height=font_height,borders='left thin, right thin, top thin, bottom thin',vert = 'center',horiz = 'center'))
    FIELDNAME_FIELDATTR_cvi =OrderedDict( [
          ('stt_not_model',{'style':center_border_style,'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('department_id',{}),
          ('loai_record',{'style':center_border_style}),
          ('categ_id',{}),
          ('thiet_bi_id',{}),
          ('tvcv_id',{'string': lambda dl_model_para: u'Loại sự cố' if  dl_model_para['loai_record'] == u'Sự Cố' else u'Loại CV/Sự vụ'}),
          ('noi_dung',{}),
          ('nguyen_nhan',{ 'string':u'Nguyên nhân','skip_field':lambda dl_model_para:  dl_model_para['loai_record'] != u'Sự Cố'}),
          ('gio_bat_dau',{'style':center_border_style,'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
          ('gio_ket_thuc',{'style':center_border_style,'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
                    ])
    Export_Para_cvi = {
        'exported_model':'cvi',
        'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_cvi,
        'gen_domain':gen_domain_cvi,
        'search_para':{'order': 'loai_record asc'},#desc
        }
    return Export_Para_cvi

def dl_cvi(dl_obj,append_domain = []):
#     font_height = 
    Export_Para_cvi = generate_Export_Para_cvi(dl_obj)
    Export_Para_cvi_copy = deepcopy(Export_Para_cvi)
    Export_Para_cvi_copy['FIELDNAME_FIELDATTR']['nguyen_nhan']['skip_field'] = False
    Export_Para_cvi_copy['FIELDNAME_FIELDATTR']['tvcv_id']['string'] = u'Loại'
    filename = 'cvi'
    name = "%s%s" % (filename, '.xls')
    wb =  download_model(dl_obj,
                         Export_Para=Export_Para_cvi_copy,
                         append_domain=append_domain
                        )
    return wb,name


def  write_before_title (kargs):
    worksheet = kargs['worksheet']
    row_index_before_title = kargs['row_index_before_title']
    col_index_before_title = kargs['col_index_before_title']
    noi_dung = kargs['noi_dung']
    style = kargs.get('style',normal_style)
    worksheet.write(row_index_before_title, col_index_before_title, noi_dung,style)
    
    
LOAI_REC_=OrderedDict([(u'Sự Cố',{'noi_dung':u'A. TÌNH HÌNH HƯ HỎNG, SỰ CỐ TRÊN MẠNG:'}),
           (u'Công Việc',{'noi_dung':u'B. TÌNH HÌNH THAY ĐỔI THIẾT BỊ VÀ DỊCH VỤ MẠNG:'})
           ])



def thuebaotable_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
    append_domain = [('date','=',dl_obj.date)]
    n_row = download_model(dl_obj,
             Export_Para=Export_Para_thuebao,
            append_domain=append_domain,
             worksheet=worksheet,
             ROW_TITLE = row_index,
             return_more_thing_for_bcn = True,
             no_gray = True,
             is_set_width = False
                             )
    return n_row 
                             
                             

def table_bcn_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
#     cates = kargs ['cates'] 
    
    font_height = dl_obj.font_height
    bold_style = xlwt.easyxf(generate_easyxf(height=font_height,bold=True)) 
    bold_italic_style = xlwt.easyxf(generate_easyxf( bold=True, height=font_height, italic=True))
    Export_Para_cvi = generate_Export_Para_cvi(dl_obj)
    Export_Para_cvi_copy1 = deepcopy(Export_Para_cvi)
    is_show_loai_record = dl_obj.env['ir.config_parameter'].sudo().get_param('dai_tgg.' + 'is_show_loai_record')
    Export_Para_cvi_copy1['FIELDNAME_FIELDATTR']['loai_record']['skip_field'] = not is_show_loai_record
    Export_Para_cvi_copy1['FIELDNAME_FIELDATTR']['categ_id']['skip_field'] = not is_show_loai_record
    nhoms = request.env['product.category'].search([('stt_for_report','!=',False)],order='stt_for_report asc')
    row_index_begin = row_index
    dl_model_para = {}
    for loai_record,attrs in LOAI_REC_.items():
            dl_model_para ['loai_record'] = loai_record
            noi_dung_1= attrs['noi_dung']
            row_index +=1
            write_before_title(
                {'worksheet' :worksheet,
                'row_index_before_title' :row_index,
                'col_index_before_title' :0,
                'noi_dung':noi_dung_1,
                'style':bold_style}
                ) # ghi A. sự cố , B. công việc
            row_index +=2
            if loai_record ==u'Công Việc':
                domain_loai_record = [('loai_record','in',[u'Công Việc',u'Sự Vụ']),('loai_cvi','!=',u'Chia Điểm Con')]
            else:
                domain_loai_record = [('loai_record','=',loai_record)]
            for cate in nhoms:# categ_id # ghi các đầu nhóm 1. IP , 2TRD
                Export_Para_cvi_copy = deepcopy(Export_Para_cvi_copy1)
                domain =[('categ_id','=',cate.id),(('is_bc','=',True))] + domain_loai_record
                n_row = download_model(dl_obj,
                             Export_Para=Export_Para_cvi_copy,
                             append_domain=domain,
                             workbook=None,
                             worksheet=worksheet,
                             ROW_TITLE = row_index ,
                             return_more_thing_for_bcn = True,
                            write_before_title = write_before_title,
                            
                            kargs_write_before_title = {'worksheet' :worksheet,
                                                                        'row_index_before_title' :row_index ,
                                                                        'col_index_before_title' :0,
                                                                        'noi_dung':u'%s/%s'%(cate.stt_for_report,cate.name),
                                                                        'style':bold_italic_style},
                             
                             dl_model_para =dl_model_para,
                             no_gray = True,
                             OFFSET_COLUMN = 0,
                             write_title_even_not_recs_for_title=True,
                             is_set_width = False,
                             
                                                               
                             )
                row_index += n_row
    return row_index- row_index_begin + 1

def hom_nay_(ws,f_name,fixups,needdata,row,dl_obj):
    return u'Ngày ' + Convert_date_orm_to_str(dl_obj.date,format_date = '%d/%m/%Y') 



def dl_bcn(dl_obj,append_domain = []):
    filename = u'Báo cáo ngày_%s' %fields.Date.from_string(dl_obj.date).strftime('%d_%m_%Y')
    name = "%s%s" % (filename, '.xls')
    set_cols_width = [4,21,8,40,20,40,30,30]
    set_cols_width = map(get_width,set_cols_width)
    font_height = dl_obj.font_height
    center_style = xlwt.easyxf(generate_easyxf(height=font_height,vert = 'center',horiz='center'))
    bold_center_style = xlwt.easyxf(generate_easyxf(height=font_height, vert = 'center',horiz = 'center',bold=True))
    fixups =[  
                 ('trung_tam1',{'range':[0,0,0,3],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('trung_tam2',{'range':[1,1,0,3],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('chxhcnvn',{'range':[0,0,4,7],'val':u'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('dltdhp',{'range':[1,1,4,7],'val':u'Độc lập - Tự do - Hạnh Phúc', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('bbg',{'range':[3,3,0,7],'val':u'BÁO CÁO THÔNG TIN', 'style':bold_center_18_style,'height':1119,'off_set':1}),
                 ('hom_nay',{'range':[4,4,0,7],'val':None, 'val_func': hom_nay_,'style':center_style }),
                 ('table',{'range':['auto', 0],'val':None,'func':table_bcn_ ,'offset':3 }),
                 ('thuebao_title',{'range':['auto', 0],'val':None,'val':u'C. TÌNH HÌNH THUÊ BAO CẬP NHẬT MẠNG DI ĐỘNG (lúc 19h00):','style':bold_style,'offset':1 }),
                 ('thuebaotable',{'range':['auto', 0],'val':None,'func':thuebaotable_ ,'offset':2}),
                 ('pho_dai_vthcm',{'range':['auto', 'auto',1,3],'val':u'Phó đài VT HCM','style':bold_center_style}),
                 ('tphcm',{'range':['auto', 'auto', 7,9],'offset':0, 'val':u'Tp. Hồ Chí Minh, Ngày %s'%Convert_date_orm_to_str(dl_obj.date),'style':bold_center_style}),
                 ('ten_pho_dai_vthcm',{'range':['auto', 'auto',1,3],'offset':5,'val':u'Nguyễn Văn Xuân','style':bold_center_style}),
                 ('ten_nguoi_bc',{'range':['auto', 'auto',7,9],'offset':0,'val':dl_obj.env.user.name,'style':bold_center_style}),
                 ]
    wb = write_all_row(fixups,dl_obj,set_cols_width)
        
    return wb,name
        
    


