# -*- coding: utf-8 -*-
# from odoo import http
# from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
# from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
# from unidecode  import 
# 
# 
# import json
# 
# class DownloadQuants(http.Controller):
#     @http.route('/web/binary/download_model',type='http', auth="public")
#     def download_all_model_controller(self,model, id, **kw):
#         active_domain = kw['active_domain']
#         active_domain = active_domain.replace("'",'"')
#         active_domain = json.loads(active_domain)
#         dj_obj = request.env['tonkho.downloadquants'].browse(int(id))
#         pick_func = {'stock.quant':download_quants,'product.product':download_product}
#         call_func = pick_func[model]
#         workbook,name = call_func(dj_obj,active_domain)
#        
#         name = unidecode(name).replace(' ','_')
#         response = request.make_response(None,
#             headers=[('Content-Type', 'application/vnd.ms-excel'),
#                     ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
#             )
#         workbook.save(response.stream)
#         return response
    