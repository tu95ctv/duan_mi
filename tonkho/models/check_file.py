# -*- coding: utf-8 -*-
from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import gen_model_dict

def check_imported_file_sml(dl_obj):
#     title_row_for_import = [dl_obj.title_row_for_import or 0]
#     md = gen_model_dict(title_row_for_import)
    workbook = importthuvien(dl_obj,
#                              model_dict = md,
                             key=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',
                             key_tram='sml',
                             check_file=True)
    filename = 'check_file_of_%s-%s'%(dl_obj.filename,dl_obj.id)
    name = "%s%s" % (filename, '.xls')
    return workbook,name
