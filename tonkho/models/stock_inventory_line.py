# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.tools import float_utils

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    categ_id = fields.Many2one('product.category', related='product_id.categ_id',store=True,string=u'Nhóm')
    thiet_bi_id = fields.Many2one('tonkho.thietbi', related='product_id.thiet_bi_id',store=True)
    brand_id = fields.Many2one('tonkho.brand', related='product_id.brand_id',store=True)
    pn = fields.Char(related='product_id.pn',store = True)
    stt = fields.Integer(string=u'STT')
    tracking =  fields.Selection(related='product_id.tracking', store=True,string=u'Có SN hay không')
    ghi_chu = fields.Text(string=u'Ghi chú')
    barcode_sn = fields.Char(related = 'prod_lot_id.barcode_sn',store=True)
    quant_ids =  fields.One2many('stock.quant','inventory_line_id')
    stock_quant_id = fields.Many2one('stock.quant', string=u"Lấy vật tư có trong kho")
    @api.onchange('stock_quant_id')
    def stock_quant_id_change_(self):
        if self.stock_quant_id:
            self.product_id = self.stock_quant_id.product_id
            self.prod_lot_id = self.stock_quant_id.lot_id
            self.location_id = self.stock_quant_id.location_id
            
            
    @api.constrains('product_id','prod_lot_id')
    def product_id_prod_lot_id_(self):
        for r in self:
            print ("r.product_id.tracking",r.product_id.tracking, r.prod_lot_id)
            if r.product_id.tracking =='serial' and  not r.prod_lot_id:
                raise UserError(u'product (%s,%s) có tracking nhưng INV line lại không có lot_id'%(r.product_id.name,r.product_id.pn))
    def _get_move_values(self,*arg,**karg):
        rs = super(InventoryLine, self)._get_move_values(*arg,**karg)
        rs['move_line_ids'][0][2]['stt'] = self.stt#self._context['stt']
        rs['move_line_ids'][0][2]['inventory_line_id'] = self.id
        return rs

    
    