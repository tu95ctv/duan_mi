# -*- coding: utf-8 -*-
# from odoo.addons.tonkho.models.dl_models.dl_model import  download_model
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_
from openerp.http import request
# 
# def stt_(v,needdata): 
#     v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
#     return v      

def pr_running_quant_(v,n,parent_location_id='parent_location_id'):
        domain_quant = [('product_id','=',n['a_instance_dict']['id']['val']),('location_id','child_of',getattr(n['dl_obj'], parent_location_id).id)]#dl_obj_global
        Quant = request.env['stock.quant']
        try:
            item = Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')[0]
            quant = item['quantity']
        except IndexError:
            quant = 0
        return quant
FIELDNAME_FIELDATTR_PRODUCT = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
         ('id',{}),
         ('name',{}),
         ('categ_id',{'func':lambda v,n: v.name}),
         ('pr_running_quant',{'is_not_model_field':True,'func':pr_running_quant_,'kargs':{'parent_location_id':'parent_location_runing_id'}}),
         ('pr_prepare_quant',{'is_not_model_field':True,'func':pr_running_quant_}),
                    ]
Export_Para_product = {
'exported_model':'product.product',
'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_PRODUCT,
'gen_domain':None,
'search_para':{'order': 'id asc'},#desc
}
    
    
def download_product(dl_obj,append_domain = []):
#     file_name = 'vat_tu_du_phong_%s_dang_chay_%s'
    file_name = u'Vật tư dự phòng %s đang chạy %s'
    filename =file_name%(dl_obj.parent_location_id.name, dl_obj.parent_location_runing_id.name)
    name = "%s.%s" % (filename, '.xls')
    wb =  download_model(dl_obj,
                         Export_Para=Export_Para_product,
                         append_domain=append_domain)
    return wb,name