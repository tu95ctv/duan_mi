# -*- coding: utf-8 -*-
# from odoo.addons.tonkho.models.dl_models.dl_model import  download_model
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_

from openerp.http import request
import xlwt
from odoo.exceptions import UserError
from copy import deepcopy

def tu_shelf_(v,needdata, stock_type=None):
    location_id = needdata['a_instance_dict']['location_id']['val_before_func']
    l_id = request.env['stock.location'].search([('id','parent_of',location_id.id),('stock_type','=',stock_type)])
    if l_id:
        return l_id[0].name

def gen_domain_stock_quant(dl_obj):
    domain = []
    if dl_obj.parent_location_id:
        domain.append(('location_id','child_of',dl_obj.parent_location_id.id))
    return domain
def tracking_(v,needdata):
    adict = {'serial':u'Có SN','none':u'Không có SN'}
    return adict[v]
    
def download_quants(dl_obj,append_domain = []):
    
    FIELDNAME_FIELDATTR_quants = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
         ('id',{}),
         ('stt',{'skip_field':not dl_obj.is_not_skip_field_stt}),
         ('product_id',{'func':lambda v,n: v.name,'string':u'Tên Vật Tư','width':30}),
         ('thiet_bi_id',{'func':lambda v,n: v.name,}),
         ('brand_id',{'func':lambda v,n: v.name}), 
         ('product_uom_id',{'string':u'ĐVT'}), 
         ('tracking',{'func':tracking_}),
         ('categ_id',{'func':lambda v,n: v.name }),
         ('pn',{}),
         ('lot_id',{'func':lambda v,n: v.name,'string':u'Serial number'}),
         
         ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
                 ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'kargs':{'stock_type':'tram'}}),         
                 ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'kargs':{'stock_type':'phong_may'}}),
                 ('tu',{'is_not_model_field':True,'string':u'Tủ/cabinet','func':tu_shelf_,'kargs':{'stock_type':'tu'}}),
                 ('shelf',{'is_not_model_field':True,'string':u'Shelf/ngăn/kệ','func':tu_shelf_,'kargs':{'stock_type':'shelf'}}),
                 ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf/số thùng','func':tu_shelf_,'kargs':{'stock_type':'stt_trong_self'}}),
                 ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'kargs':{'stock_type':'slot'}})     
             ]}),
                                  
         ('location_id_complete',{'transfer_fname':'location_id','string':'kho tên đầy đủ','func':lambda v,n: v.name_get_1_record()}),
          ('quantity',{'string':u'Số lượng'}),
          ('qty_dieu_chinh',{'transfer_fname':'quantity','string':u'Số lượng điều chỉnh','skip_field':not dl_obj.is_xuat_dc}),
         ('tram_dc',{'is_not_model_field':True,'string':u'Trạm điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc}),         
         ('phong_may_dc',{'is_not_model_field':True,'string':u'Phòng máy điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc}),
         ('tu_dc',{'is_not_model_field':True,'string':u'Tủ điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc}),
         ('shelf_dc',{'is_not_model_field':True,'string':u'Shelf điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc}),
         ('stt_trong_self_dc',{'is_not_model_field':True,'string':u'STT trong shelf điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc}),
         ('slot_dc',{'is_not_model_field':True,'string':u'Slot điều chuyển','skip_field':not dl_obj.is_xuat_kho_dc})     
                 
                 
                    ]
    Export_Para_quants = {
        'exported_model':'stock.quant',
        'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_quants,
        'gen_domain':gen_domain_stock_quant,
#         'search_para':{'order': 'stt asc'},#desc
        }
    
    if not dl_obj.is_moi_sheet_moi_loai:
        filename = u'Số lượng trong kho %s'%dl_obj.parent_location_id.name
        name = "%s%s" % (filename, '.xls')
        workbook =  download_model(dl_obj,
                             Export_Para=Export_Para_quants,
                             append_domain=append_domain
                            )
    else:
        filename = u'Số lượng trong kho phân_nhóm %s'%dl_obj.parent_location_id.name
        name = "%s%s" % (filename, '.xls')
        Quant = request.env['stock.quant']#.search([])
        tram_domain = gen_domain_stock_quant(dl_obj)
#         cates = Quant.search(append_domain + tram_domain).mapped('categ_id')
        cates = Quant.search(append_domain + tram_domain).sorted(key=lambda r: r.categ_id.stt_for_report).mapped('categ_id')
        workbook = xlwt.Workbook()
        for cate in cates:
            Export_Para_quants_copy = deepcopy(Export_Para_quants)
            domain =[('categ_id','=',cate.id)]
            if append_domain:
                domain.extend(append_domain)
            download_model(dl_obj,
                         Export_Para=Export_Para_quants_copy,
                         append_domain=domain,
                         workbook=workbook,
                         sheet_name=cate.name)
    return workbook,name
        
    


