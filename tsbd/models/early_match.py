# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import  timedelta
import datetime

class EarlyMatch(models.Model):
    _name = 'tsbd.ematch'
    match_ids = fields.Many2many('tsbd.match',compute='match_ids_')
    

    def match_ids_(self):
        match_ids = self.env['tsbd.match'].search([('date','=' ,fields.Date.to_string(datetime.date.today()))])
        self.match_ids = match_ids