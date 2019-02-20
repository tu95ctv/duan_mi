# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import name_compute,Convert_date_orm_to_str,name_khong_dau_compute


# class NameKhongDau(models.Model):
#     _name = 'dai_tgg.namekhongdau'
#     _auto = False
#     name = fields.Char()
#     name_khong_dau = fields.Char(compute='name_khong_dau_', store=True)
#     name_viet_tat =  fields.Char(compute='name_khong_dau_', store=True)
#     @api.depends('name')
#     def name_khong_dau_(self):
#         name_khong_dau_compute(self)


class ToTrinh(models.Model):
    _name = 'dai_tgg.totrinh'
    _inherit = ['khongdaumodel']
    _auto = True
#     _rec_name = 'complete_name'
    ve_viec = fields.Char(u'Về việc',required=True)
    so_to_trinh = fields.Char(string=u'Số')
    ngay_to_trinh = fields.Date(string=u'Ngày')
    name = fields.Char(compute='complete_name_',store=True, string=u'Tên')
    file_ids =  fields.Many2many('dai_tgg.file','to_trinh_file_relate','to_trinh_id','file_id',string=u'File')
    
    
    
    
    
    
    @api.multi
    def name_get(self):
        return [(r.id, r.get_names()) for r in self]
    def get_names(self):
        complete_name =  name_compute(self,join_char = u' - ',junc_char=u':',
            adict=[
                    ('so_to_trinh',{'pr':u'Số'}),
                   ('ngay_to_trinh',{'pr':u'Ngày','func':Convert_date_orm_to_str,'karg':{'format_date':'%d/%m/%Y'}}),
                   ('ve_viec',{'pr':u'V/v'}),
                   ]
                                 )
        return complete_name
    
    
    def get_names_for_report(self):
        name =  name_compute(self,join_char = u', ',junc_char=u'',
            adict=[
                    ('so_to_trinh',{'pr':u'số'}),
                   ('ngay_to_trinh',{'pr':u'ngày','func':Convert_date_orm_to_str,'karg':{'format_date':'%d/%m/%Y'}}),
                   ('ve_viec',{'pr':u'V/v'}),
                   ]
                                 )
        return name
    
    @api.depends('ve_viec','so_to_trinh','ngay_to_trinh')
    def complete_name_(self):
        for r in self:
            r.name = r.get_names()
            
            
#             r.complete_name =  name_compute(r,join_char = u' ',junc_char=u'',
#             adict=[
#                     ('so_to_trinh',{'pr':u'Số'}),
#                    ('ngay_to_trinh',{'pr':u'Ngày','func':Convert_date_orm_to_str,'karg':{'format_date':'%d/%m/%Y'}}),
#                    ('name',{'pr':u'V/v'}),
#                    ]
#                                  )
    