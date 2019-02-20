# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
from odoo.addons.tonkho.models.dl_models.xl_tranfer_bb import write_xl_bb
import datetime

from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.tonkho.models.check_file import check_imported_file_sml


from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
from unidecode  import unidecode
import json
from odoo.addons.downloadwizard.download_tool import  download_all_model_by_url

class DownloadQuants(http.Controller):
    @http.route('/web/binary/download_model/tonkho',type='http', auth="public")
    def download_all_model_controller(self,**kw):
        response = download_all_model_by_url(kw)
        return response
#     
# 
#     @http.route('/web/binary/download_xl_bbbg',type='http', auth="public")
#     def download_xl_bbbg_by_new_window(self,model, id, **kw):
#         model = 'stock.picking'
#         dj_obj = request.env[model].browse(int(id))
#         workbook,name = write_xl_bb(dj_obj)
#         response = request.make_response(None,
#             headers=[('Content-Type', 'application/vnd.ms-excel'),
#                     ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
#             )
#         workbook.save(response.stream)
#         return response
#     
#     
#     @http.route('/web/binary/download_checked_import_sml_file',type='http', auth="public")
#     def download_checked_import_sml_file(self,model, id, **kw):
#         dj_obj = request.env[model].browse(int(id))
#         wb,name= check_imported_file_sml(dj_obj)
#         response = request.make_response(None,
#             headers=[('Content-Type', 'application/vnd.ms-excel'),
#                     ('Content-Disposition', 'attachment; filename=%s;target=blank'%name)],
#             )
#         wb.save(response.stream)
#         return response
#     
    
    
    
    