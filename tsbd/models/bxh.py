# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.tool import  request_html
from bs4 import BeautifulSoup

class BXH(models.Model):
    _name = 'tsbd.bxh'
    _order = 'diem desc, hsbt desc, score_sum desc'
    leech_ids = fields.Many2many('tsbd.leech','leech_bxh_rel', 'bxh_id', 'leech_id')
    team_id = fields.Many2one('tsbd.team')
    stt = fields.Integer()
    cate_id = fields.Many2one('tsbd.cate')
    home_t = fields.Integer()
    home_h = fields.Integer()
    home_b = fields.Integer(compute='home_b_', store=True)
    @api.depends('home_match_number','home_t','home_h')
    def home_b_(self):
        for r in self:
            r.home_b = r.home_match_number - r.home_t -  r.home_h
            
    home_tg = fields.Integer()
    home_th = fields.Integer()
    home_match_number =  fields.Integer()
    
    away_t = fields.Integer()
    away_h = fields.Integer()
    away_b = fields.Integer(compute='away_b_', store=True)
    @api.depends('away_match_number','away_t','away_h')
    def away_b_(self):
        for r in self:
            r.away_b = r.away_match_number - r.away_t -  r.away_h
            
    away_tg = fields.Integer()
    away_th = fields.Integer()
    away_match_number =  fields.Integer()
    diem = fields.Integer(compute='diem_', store=True)
    diem_dd = fields.Integer()
    score_sum = fields.Integer(compute='score_sum_',store=True)
    lost_score_sum = fields.Integer(compute='score_sum_',store=True)
    @api.depends('away_tg','home_tg')
    def score_sum_(self):
        for r in self:
            r.score_sum = r.away_tg + r.home_tg
            r.lost_score_sum = r.away_th + r.home_th
            
    hsbt = fields.Integer(compute='hsbt_', store=True)
    @api.depends('away_tg','home_tg','away_th','home_th')
    def hsbt_(self):
        for r in self:
            r.hsbt =  r.away_tg + r.home_tg - r.away_th - r.home_th
            
    match_number =  fields.Integer(compute='match_number_',store=True)
    
    @api.depends('home_match_number', 'away_match_number')
    def match_number_(self):
        for r in self:
            r.match_number = r.home_match_number + r.away_match_number

    
    
    @api.depends('home_t','home_h', 'away_t', 'away_h')
    def diem_(self):
        for r in self:
            r.diem = (r.home_t + r.away_t) *3 + (r.home_h + r.away_h)
    
    