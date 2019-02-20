# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
import re
from odoo.addons.dai_tgg.mytools import pn_replace


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _sql_constraints = [
#         ('name_ref_uniq', 'unique (name, product_id)', 'The combination of serial number and product must be unique !'),
#         ('name_ref_uniq', 'unique (name, product_id,barcode_sn)', 'The combination of serial number and product must be unique !'),
        ('name_ref_uniq', 'unique (name)', 'The serial number must be unique !'),

    ]
#     _rec_name = 'complete_name'
    name = fields.Char(
        'Lot/Serial Number', 
        default = False,
        required=True, help="Unique Lot/Serial Number")
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],
                                  default='tot',
                                  store=True,
                                   string=u'Tình trạng')
    pn = fields.Char(related='product_id.pn',string=u'Part number',store=True)
    name_replace = fields.Char(compute='name_replace_',store=True)
    quant_ids = fields.One2many('stock.quant', 'lot_id',domain=[('location_id.usage','=','internal')],string=u'Trong kho')#domain=[('location_id.usage','=','internal')]
    ghi_chu = fields.Text(string=u'Ghi chú từ dòng điều chuyển')
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi Chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    id_ke_toan = fields.Char(string=u'ID kế toán')
    the_tai_san = fields.Char(string=u'Thẻ tài sản')
    ngay_su_dung = fields.Date(string=u'Ngày sử dụng')
    #chưa xài
    barcode_sn = fields.Char()
    
    ml_ids = fields.One2many('stock.move.line','lot_id',compute='ml_ids_',string=u'Các dòng điều chỉnh')
    @api.depends('is_done_ml_filter','is_your_department_filter','id_show')
    def ml_ids_(self):
        for r in self:
            active_id = r.id_show
            domain = [('lot_id','=',active_id)]# r.id = new object nên không được
            if r.is_done_ml_filter:
                domain.append(('state','=','done'))
            if r.is_your_department_filter:
                your_department_id = self.env.user.department_id.id
                department_domain = ['|',('location_id.department_id','=',your_department_id),('location_dest_id.department_id','=',your_department_id)]
                domain.extend(department_domain)
            r.ml_ids = self.env['stock.move.line'].search(domain,order='id desc')
            
    is_done_ml_filter =  fields.Boolean(default= True,store=False, string=u'Chỉ lọc dòng hoàn thành')
    is_your_department_filter =  fields.Boolean(default= True,store=False,string =u'Chỉ lọc kho  đơn vị của bạn')
    id_show =  fields.Integer(compute='id_show_')
    def id_show_(self):
        for r in self:
            r.id_show = r.id
    
    

    @api.depends('name')
    def name_replace_(self):
        for r in self:
            if r.name:
#                 r.name_replace = re.sub('[-_ \s]','',r.name)
                r.name_replace = pn_replace(r.name)
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
#             name_replace = re.sub('[-_ \s]','',name)
            name_replace = pn_replace(name)
        else:
            name_replace = ''
        recs = self.search(['|',('name', operator, name), ('name_replace', operator, name_replace)] + args, limit=limit)
        return recs.name_get()
    
    
    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('lot_id', '=', self.id)]
        return action

    

   
                
                
