# -*- coding: utf-8 -*-
from odoo import models, fields, api#,tools
from odoo.exceptions import UserError#, except_orm
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
import psycopg2
from unidecode import unidecode
from odoo.addons.dai_tgg.mytools import name_khong_dau_compute
   

class ProductTemplate(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = 'product.template'
    name = fields.Char('Name', index=True, required=True, translate=False)
    type = fields.Selection(selection_add=[],default = 'product')
    thiet_bi_id = fields.Many2one('tonkho.thietbi', string = u'Thiết bị',ondelete="restrict")
    brand_id = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất')
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    quant_ids = fields.One2many('stock.quant', 'product_id',domain=[('location_id.usage','=','internal')],string=u'Trong kho')#domain=[('location_id.usage','=','internal')]
    stock_location_id_selection = fields.Selection('get_stock_for_selection_field_', store=False)
    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate,self).default_get(fields)
        uom_id= self.env['product.uom'].search([('name','=',u'Cái')]).id
        res['uom_id'] = uom_id
        return res
    name_khong_dau = fields.Char(compute='name_khong_dau_',store=True)
    name_viet_tat = fields.Char(compute='name_khong_dau_',store=True)
    @api.depends('name')
    def name_khong_dau_(self):
        name_khong_dau_compute(self)
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        recs = self.search(['|',('name', operator, name), ('name_khong_dau', operator, name)],args, limit=limit)
        return recs.name_get()
    def get_stock_for_selection_field_(self):
        locs = self.env['stock.location'].search([('is_kho_cha','=',True)])
        rs = list(map(lambda i:(i.name,i.name),locs))
        return rs
    def write(self, vals):
        return super(ProductTemplate, self.with_context(search_move_line_in_write=1)).write(vals) # vi sao phai lam vay --> de change uom cua PT
    

        