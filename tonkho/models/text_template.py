# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TextTemplate(models.Model):
    _name = 'tonkho.texttemplate'
    name = fields.Char()
    field_context = fields.Char()