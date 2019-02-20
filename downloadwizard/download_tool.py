from unidecode  import unidecode
import json
from openerp.http import request
from odoo import fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError
def do_if_model_name_wrapper(model_name):
    def do_if_model_name(func):
        def f_wrapper(self):
            if self.model_name ==model_name:
                func(self)
            else:
                pass
        return f_wrapper
    return do_if_model_name


def download_all_model_by_url(kw):
#     active_domain = kw['active_domain']
    downloadwizard_id = kw.get('downloadwizard_id')
    active_domain = kw.get('active_domain')
    download_key = kw.get('download_key')
    
    if active_domain:
        active_domain = active_domain.replace("'",'"')
        active_domain = json.loads(active_domain)
    if downloadwizard_id:
        dj_obj = request.env['downloadwizard.download'].browse(int(downloadwizard_id))
        download_key =  dj_obj.model_name
    else:
        download_model = kw.get('download_model')
        download_model_id = kw.get('download_model_id')
        dj_obj = request.env[download_model].browse(int(download_model_id))
    
    pick_func = request.env['downloadwizard.download'].gen_pick_func()
    call_func = pick_func[download_key]
    print ('pick_func dict',pick_func,'download_key',download_key)
    if active_domain:
        workbook,name = call_func(dj_obj,active_domain)
    else:
        workbook,name = call_func(dj_obj)
#     name = 
    print ('name***',name)
    name = unidecode(name).replace(' ','_')
#     now = datetime.now() + timedelta(hours=7)
#     format='%d_%m_%Y_%H_%M' 
#     now = now.strftime(format)
#     name +='_' + now
    
    response = request.make_response(None,
        headers=[('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
        )
    workbook.save(response.stream)
    return response