# -*- coding: utf-8 -*-
from odoo import models, fields, api#,tools
from odoo.exceptions import UserError#, except_orm
from odoo.addons.dai_tgg.mytools import name_khong_dau_compute
import re

class Categ(models.Model):
    _inherit = 'product.category'
    stt_for_report = fields.Integer(u'STT cho báo cáo ngày')
    name_khong_dau = fields.Char(compute='name_khong_dau_',store=True)
    name_viet_tat = fields.Char(compute='name_khong_dau_',store=True)
    @api.depends('name')
    def name_khong_dau_(self):
        name_khong_dau_compute(self)
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(['|',('name', operator, name), ('name_khong_dau', operator, name)] + args, limit=limit)
        return recs.name_get()
class ThietBi(models.Model):
    _name = 'tonkho.thietbi'
    name = fields.Char(required=True)
    brand_id = fields.Many2one('tonkho.brand',ondelete="restrict",string=u'Hãng sản xuất')
    categ_id = fields.Many2one(
        'product.category', u'Nhóm',ondelete="restrict")
class Brand(models.Model):
    _name = 'tonkho.brand'
    name = fields.Char(required=True)
   