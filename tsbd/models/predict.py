# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.bet import handicap_winning_ 

class Predictsite(models.Model):
    _name = 'tsbd.site'
    name = fields.Char()
    
class Predict(models.Model):  
    _name =  'tsbd.predict'
#     _inherit = 'tsbd.bet'
    match_id = fields.Many2one('tsbd.match')
    site_id = fields.Many2one('tsbd.site',string='web site')
    predict_score1 = fields.Integer()
    predict_score2 = fields.Integer()
    predict_handicap = fields.Selection([('handicap1','handicap1'),('handicap2','handicap2')],compute='predict_handicap_and_ou_',store=True)
    amount = fields.Float(default=1)
    predict_exact_score_winning_amount =  fields.Float(compute='predict_exact_score_winning_amount_',store=True)
    
    
    @api.depends('predict_score1','predict_score2')
    def predict_exact_score_winning_amount_(self):
        for r in self:
            bet_kind = 'exact_score'
            winning_ratio,winning_amount = handicap_winning_(r,bet_kind,mode='predict')
            r.predict_exact_score_winning_amount = winning_amount
            
    
    @api.depends('match_id.begin_ou','match_id.begin_handicap','predict_score1','predict_score2')
    def predict_handicap_and_ou_(self):
        for r in self:
#             r.bet_score1 = r.predict_score1
#             r.bet_score2 = r.predict_score2
#             r.bet_kind = 'exact_score'
            diff = (r.predict_score1 - r.predict_score2) - r.match_id.begin_handicap
            if diff > 0:
                predict_handicap = 'handicap1'
            else:
                predict_handicap = 'handicap2'
            r.predict_handicap = predict_handicap
            
            sum_score = r.predict_score1 + r.predict_score2
            if sum_score > r.match_id.begin_ou:
                predict_ou = 'over'
            else:
                predict_ou = 'under'
            r.predict_ou = predict_ou
    predict_ou = fields.Selection([('over','over'),('under','under')],compute='predict_handicap_and_ou_',store=True)
    predict_handicap_winning_mount = fields.Float(compute='predict_handicap_winning_mount_',store=True)
    predict_ou_winning_mount = fields.Float(compute='predict_ou_winning_mount_',store=True)
    

    @api.depends('predict_ou')
    def predict_ou_winning_mount_(self):
        for r in self:
#             r.ou = r.match_id.begin_ou
            bet_kind = r.predict_ou
            winning_ratio,winning_amount = handicap_winning_(r,bet_kind,mode='predict')
            r.predict_ou_winning_mount = winning_amount
    @api.depends('predict_handicap')
    def predict_handicap_winning_mount_(self):
        for r in self:
#             r.handicap = r.match_id.begin_handicap
            bet_kind = r.predict_handicap
            winning_ratio,winning_amount = handicap_winning_(r,bet_kind,mode='predict')
            r.predict_handicap_winning_mount = winning_amount
            
            
            

    
    
class Event(models.Model):
    _name = 'tsbd.event'
    time = fields.Datetime(default=fields.Datetime.now)
    match_id = fields.Many2one('tsbd.match')
    event = fields.Selection([('reset_score','reset_score'),('goal1','goal1'),('goal2','goal2'),('corner1','corner1'),('corner2','corner2')])
    score1 = fields.Integer()
    score2 = fields.Integer()
    current_time = fields.Float()
    
    
    @api.onchange('time')
    def _oc_time(self):
        current_time = fields.Datetime.from_string(self.time) - fields.Datetime.from_string(self.match_id.time)
        current_time = current_time.seconds/60
        if current_time > 47:
            current_time =current_time - 15
        self.current_time = current_time
    
    @api.onchange('current_time')
    def _oc_current_time(self):
        current_time = self.current_time
        current_time = current_time + 15 if current_time > 47 else current_time
        self.time = fields.Datetime.from_string(self.match_id.time)  +  timedelta(minutes=current_time)
        
    @api.onchange('event')
    def _oc_event(self):
        score1 = self._context.get('default_score1')
        score2 = self._context.get('default_score2')
        if score1 !=None and score2!=None:
            if self.event =='goal1':
                score1 = score1 +1
                score2 = score2
            elif self.event =='goal2':
                score1 = score1
                score2 = score2 + 1
            self.score1 = score1
            self.score2 = score2
            
            
