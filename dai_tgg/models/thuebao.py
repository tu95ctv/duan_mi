# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
adict = {
'MSSE2D':1,
'MSSE2G':2,
'MSS2F':3,
'MSSE2E':4,
'MSSE2F':5,
'MSS2C':6,
'TSS2A':7,
'TSC2B':8,
'SGSN2B':9,
'SGSN2C':10,
}

aselect =  (list(map(lambda i:(i,i),sorted(adict, key=adict.__getitem__))))

class Thuebaoline(models.Model):
    _name = 'dai_tgg.thuebaoline'
    msc = fields.Selection(aselect)
    tb_cap_nhat =  fields.Integer(u'TB cập nhật')
    tb_mo_may =  fields.Integer(u'TB mở máy')
    tb_tat_may =  fields.Integer(u'TB tắt máy')
    tai_cp =  fields.Integer(u'Tải CP')
    date = fields.Date(compute='date_',store=True,readonly=False,string=u'Ngày')
    @api.depends('thuebao_id.date')
    def date_(self):
        for r in self:
#             print ('***1',r.thuebao_id,r.thuebao_id.date)
#             if r.thuebao_id: # Nếu không có dòng này thì khi sửa vẫn có giá trị củ
#                 print ('***2',r.thuebao_id,r.thuebao_id.date)
                r.date = r.thuebao_id.date
    stt =  fields.Integer('STT')
    thuebao_id = fields.Many2one('dai_tgg.thuebao')
    
#     @api.multi
#     def write(self,vals):
#         print ('write vals***',vals)
#         res= super(Thuebaoline, self).write(vals)
#         return res
        
    
class Thuebao(models.Model):
    _name = 'dai_tgg.thuebao'
#     _rec_name = 'date'
    date = fields.Date(required=True)
    name =  fields.Char(compute='name_')
    thuebaoline_ids =  fields.One2many('dai_tgg.thuebaoline','thuebao_id',copy=True,string=u'Các dòng thuê bao')
    @api.depends('date')
    def name_(self):
        for r in self:
            if r.date:
                r.name = fields.Date.from_string(r.date).strftime('%d/%m/%Y')
    
