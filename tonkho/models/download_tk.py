# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
# from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.tonkho.models.dl_models.xl_tranfer_bb import write_xl_bb
from odoo.addons.tonkho.models.check_file import check_imported_file_sml
from odoo.addons.downloadwizard.download_tool import  do_if_model_name_wrapper


class KhoLine(models.TransientModel):
    _name = 'tonkho.kholine'
    location_id = fields.Many2one('stock.location')
    categ_id = fields.Many2one('product.category')
    name_categ =  fields.Char(string=u'Tiêu chí')
    quantity = fields.Integer(string=u'Tổng Số lượng vật tư')
#     download_id = fields.Many2one('downloadwizard.download')
    
    
    
class DownloadQuants(models.TransientModel):
    _inherit = "downloadwizard.download"
    
    parent_location_id =  fields.Many2one('stock.location',
                                        default=lambda self:self.env.user.department_id.default_location_id.id, string=u'Kho cha dự phòng'
                                          )
    parent_location_runing_id =  fields.Many2one('stock.location',
                                                default=lambda self:self.env.user.department_id.default_location_running_id.id,
                                                 string=u'Kho đang chạy'
                                                 )
    
    is_xuat_dc =  fields.Boolean(u'Xuất cột số lượng điều chỉnh',default=True)
    is_xuat_kho_dc =  fields.Boolean(u'Xuất cột kho điều chỉnh',default=True)
#     line_ids = fields.One2many('tonkho.kholine','download_id',string=u'nhóm vật tư và số lượng trong kho')
    kho_line_ids = fields.Many2many('tonkho.kholine','wizard_dl_kholine_relate','wz_id','kl_id',compute='kho_line_ids_',string=u'nhóm vật tư và số lượng trong kho')



    @api.depends('parent_location_id')
    @do_if_model_name_wrapper('stock.quant')
    def kho_line_ids_(self):
        parent_location_id = self.parent_location_id.id
        domain = [('location_id','child_of',parent_location_id)]
        read_group_rs = self.env['stock.quant'].read_group(domain,['categ_id','quantity'],['categ_id'])
        rs = list(map(lambda i:[0,0,{'location_id':parent_location_id,'quantity':i['quantity'],'name_categ':i['categ_id'][1]}],read_group_rs))
        read_group_rs = self.env['stock.quant'].read_group(domain,['categ_id','quantity'],[])
        rs.append((0,0,{'location_id':parent_location_id,'name_categ':u'Tổng cộng', 'quantity':read_group_rs[0]['quantity']}))
        self.kho_line_ids =rs
        
        
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadQuants, self).gen_pick_func()
        pick_func = {'stock.quant':download_quants,'product.product':download_product,'write_xl_bb':write_xl_bb,'check_imported_file_sml':check_imported_file_sml}
        rs.update(pick_func)
        return rs
    @api.multi
    def gen_model_verbal_dict(self): 
        adict =  {'stock.quant':u'Kho','product.product':u'Vật tư'}
        rs = super(DownloadQuants, self).gen_model_verbal_dict()
        rs.update(adict)
        return rs
    