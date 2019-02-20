# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
class File(models.Model):
    _name = 'dai_tgg.file'
    name = fields.Char(string=u'Tên file')
    file = fields.Binary( attachment=True)
    mo_ta = fields.Text(string=u'Mô tả file')
    image = fields.Binary( attachment=True,string=u'Hình ảnh')
    image_2 = fields.Binary( attachment=True, string=u'Hình ảnh 2')
    image_3 = fields.Binary( attachment=True, string=u'Hình ảnh 3')
