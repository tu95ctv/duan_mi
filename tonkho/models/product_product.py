# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from lxml import etree
import os,inspect,sys
import datetime
from odoo.osv.orm import setup_modifiers
import re
from odoo.addons.dai_tgg.mytools import pn_replace


class TocDoXFP(models.Model):
    _name = 'tonkho.tocdo'
    name = fields.Char(required=True)
class Product(models.Model):
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name,pn)', 'The serial number must be unique !'),
    ]
    _inherit = "product.product"
    
    # field ghi đè
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
#         ('lot', 'By Lots'),
        ('none', 'No Tracking')],required=True,
                                compute='tracking_',
                                store=True,
                                string=u'Có SN hay không',
                                default='none'
                                )
    
    @api.depends('sn_ids')
    def tracking_(self):
        print ('in tracking_')
        for r in self:
            rs = self.env['stock.production.lot'].search([('product_id','=',r.id)], limit=1)
            r.tracking = 'serial' if rs else 'none'
            
            
    # field mới
    invisible_toc_do_field = fields.Boolean(compute='invisible_toc_do_field_')
    @api.depends('categ_id')
    def invisible_toc_do_field_(self):
        for r in self:
            r.invisible_toc_do_field = False if r.categ_id.name ==u'XFP, SFP' else True
#     ml_ids = fields.One2many('stock.move.line','product_id',compute='ml_ids_')
#     def ml_ids_(self):
#         for r in self:
#             r.ml_ids = self.env['stock.move.line'].search([('product_id','=',r.id),(('location_id.usage','=','internal'))])
        
    
    toc_do_id = fields.Many2one('tonkho.tocdo',string=u'Tốc độ')
    lot_ids = fields.One2many('stock.production.lot','product_id',string=u'Serial numbers')
    pn = fields.Char(string='Part number')
    pn_replace = fields.Char(compute='pn_replace_',store=True)
    qty_available_dai_hcm = fields.Float(
        u'Số lượng dự phòng trong Đài HCM', compute='qty_available_du_phong_',
        digits=dp.get_precision('Product Unit of Measure'))
    
    

            
            
#     @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
#     def _compute_quantities_dai_hcm(self):
#         dhcm =  self.env['stock.location'].search([('name','=',u'Đài HCM dự phòng')]).id
#         if not dhcm:
#             raise UserError(u'không có dhcm')
#         all_tram = self.env['stock.location'].search([('id','child_of',dhcm),('stock_type','=',u'tram')]).ids
#         if not all_tram:
#             raise UserError(u'all_tram')
#         
#         res =self.with_context(location=all_tram)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
#         for product in self:
#             kq = res[product.id]['qty_available']
#             product.qty_available_dai_hcm = kq
    
    
    qty_available_du_phong = fields.Float(
        'Quantity On Hand dự phòng', compute='qty_available_du_phong_',
        digits=dp.get_precision('Product Unit of Measure'))
    qty_available_dang_chay = fields.Float(
        'Quantity On Hand đang chạy', compute='qty_available_du_phong_',
        digits=dp.get_precision('Product Unit of Measure'))
    
    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def qty_available_du_phong_(self):
        your_location_id = self.env.user.department_id.default_location_id.id
        default_location_running_id = self.env.user.department_id.default_location_running_id.id
        dhcm =  self.env['stock.location'].search([('name','=',u'Đài HCM dự phòng')]).id
#         if not dhcm:
#             raise UserError(u'không có dhcm')
        all_tram = self.env['stock.location'].search([('id','child_of',dhcm),('stock_type','=',u'tram')]).ids
#         if not all_tram:
#             raise UserError(u'all_tram')
        res =self.with_context(location=your_location_id)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        res_runing =self.with_context(location=default_location_running_id)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        res_all_tram =self.with_context(location=all_tram)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in self:
            product.qty_available_du_phong =  res[product.id]['qty_available']
            product.qty_available_dang_chay = res_runing[product.id]['qty_available']
            product.qty_available_dai_hcm = res_all_tram[product.id]['qty_available']
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Product, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type !='search':
            doc = etree.XML(res['arch'])
            kho_du_phong_name = self.env.user.department_id.default_location_id.name
            nodes =  doc.xpath("//field[@name='qty_available_du_phong']")
            nodes[0].set('string',u'Số lượng trong %s'%kho_du_phong_name)
            
            kho_dang_chay_name = self.env.user.department_id.default_location_running_id.name
            nodes =  doc.xpath("//field[@name='qty_available_dang_chay']")
            nodes[0].set('string',u'Số lượng trong %s'%kho_dang_chay_name)
            
            
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
        
        
    
    
    @api.depends('name')
    def pn_replace_(self):
        for r in self:
            if r.pn:
                r.pn_replace = pn_replace(r.pn)
    sn_ids = fields.One2many('stock.production.lot','product_id',string='Serial numbers')
   

    @api.multi
    def name_get(self):
        result = []
        if self._context.get('show_pn_in_lot_id_name_get'):
            for r in self:
                    result.append((r.id, "%s%s" % (r.name, u' [PN:%s]'%r.pn if r.pn  else '')))
        else:
            result = super(Product, self).name_get()
        return result
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            pn_replace_str = pn_replace(name)
            domain = ['|',('name', operator, name),('pn_replace',operator,pn_replace_str)] 
        else:
            domain = []
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
#     def _get_domain_locations(self):
#         default_location_name = self.env.user.department_id.default_location_id.name
#         if default_location_name:
#             return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
#         else:
#                 raise UserError (u'default_location_name Không Có')
            
            
