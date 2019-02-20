# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
class Partner(models.Model):
    _inherit = ['res.partner']#,'khongdaumodel']
    _auto = True
    department_id = fields.Many2one('hr.department',string=u'Đơn vị')
    