# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

sign = lambda x: (1, -1)[x < 0]
# def handicap_winning_(r,bet_kind,mode='bet'):#winning_difference,money1,money2
#         last_score1 = r.match_id.score1
#         last_score2 = r.match_id.score2
#         if bet_kind =='exact_score':
#             if mode=='bet':
#                 bet_score1 = r.bet_score1
#                 bet_score2 = r.bet_score2
#             elif mode =='predict':
#                 bet_score1 = r.predict_score1
#                 bet_score2 = r.predict_score2
#             winning_difference = (bet_score1 ==last_score1) and  (bet_score2 ==last_score2) or -1
#             money1 = 'exact_money'
#             money2 = None
#         elif 'handicap' in bet_kind:
#             if mode=='bet':
#                 score1 = r.score1
#                 score2= r.score2
#                 handicap = r.handicap
#             elif mode =='predict':
#                 score1 = 0
#                 score2= 0
#                 handicap = r.match_id.begin_handicap
#             winning_difference = (last_score1 - score1) - (last_score2-score2) - handicap
#             money1 = 'handicap_money1'
#             money2 = 'handicap_money2'
#         else:# ou
#             if mode=='bet':
#                 ou =r.ou
#             elif mode =='predict':
#                 ou = r.match_id.begin_ou
#                 
#             winning_difference = (last_score1 + last_score2) - ou
#             money1 = 'ou_money1'
#             money2 = 'ou_money2'
#         dau = sign(winning_difference)
#         winning_difference_abs = abs(winning_difference)
#         if winning_difference_abs ==0.25:
#             winning_difference_abs = 0.5
#         elif winning_difference_abs ==0:
#             winning_difference_abs =0
#         else:
#             winning_difference_abs =1
#             
#             
#         winning_ratio = dau*winning_difference_abs
#         
#         if bet_kind =='handicap2' or bet_kind =='under':
#             winning_ratio = -1*winning_ratio
#             money = money2
#         else:
#             money = money1
#             
#         
#         
#         if bet_kind=='exact_score':
#             
#             if winning_ratio ==-1:
#                 handicap_money =1
#             else:
#                 if mode=='bet':
#                     handicap_money = getattr(r,money)
#                 else:
#                     handicap_money = 10
#         else:
#             if mode=='bet':
#                 handicap_money_get_obj =r
#             elif mode =='predict':
#                 money ='begin_' +money
#                 handicap_money_get_obj =r.match_id
#             handicap_money = getattr(handicap_money_get_obj,money)
#             handicap_money = handicap_money/100    
#             if winning_ratio > 0: # thắng
#                 if handicap_money < 0:
#                     handicap_money = 1
#             else: # thua
#                 if handicap_money < 0:
#                     handicap_money = abs(handicap_money)
#                 else:
#                     handicap_money = 1
# #         r.winning_ratio = winning_ratio
#         winning_amount = winning_ratio * r.amount*handicap_money
#         return winning_ratio,winning_amount
# #         r.winning_amount = winning_ratio * r.amount*handicap_money



def handicap_winning_(r, bet_kind='handicap1',mode='bet', match_id =None, skip_tinh_tien=False):#winning_difference,money1,money2
        if r !=None:
            match_id =r.match_id
            amount = r.amount
        else:
            amount = 1
        last_score1 = match_id.score1
        last_score2 = match_id.score2
        if bet_kind =='exact_score':
            if mode=='bet':
                bet_score1 = r.bet_score1
                bet_score2 = r.bet_score2
            elif mode =='predict':
                bet_score1 = r.predict_score1
                bet_score2 = r.predict_score2
            winning_difference = (bet_score1 ==last_score1) and  (bet_score2 ==last_score2) or -1
            money1 = 'exact_money'
            money2 = None
        elif 'handicap' in bet_kind:
            if mode=='bet':
                score1 = r.score1
                score2= r.score2
                handicap = r.handicap
            elif mode =='predict':
                score1 = 0
                score2= 0
                handicap = match_id.begin_handicap
            winning_difference = (last_score1 - score1) - (last_score2-score2) - handicap
            money1 = 'handicap_money1'
            money2 = 'handicap_money2'
        else:# ou
            if mode=='bet':
                ou =r.ou
            elif mode =='predict':
                ou = match_id.begin_ou
            winning_difference = (last_score1 + last_score2) - ou
            money1 = 'ou_money1'
            money2 = 'ou_money2'
        dau = sign(winning_difference)
        winning_difference_abs = abs(winning_difference)
        if winning_difference_abs ==0.25:
            winning_difference_abs = 0.5
        elif winning_difference_abs ==0:
            winning_difference_abs =0
        else:
            winning_difference_abs =1
        winning_ratio = dau*winning_difference_abs
       
        # tính tiền
        if bet_kind =='handicap2' or bet_kind =='under':
            winning_ratio = -1*winning_ratio
            money_key = money2
        else:
            money_key = money1
       
        if not skip_tinh_tien:
            if bet_kind=='exact_score':
                if winning_ratio ==-1:
                    ti_le_money =1
                else:
                    if mode=='bet':
                        ti_le_money = getattr(r, money_key)
                    else:
                        ti_le_money = 10
            else:
                if mode=='bet':
                    ti_le_money_get_obj =r
                elif mode =='predict':
                    money_key ='begin_' + money_key
                    ti_le_money_get_obj =match_id
                ti_le_money = getattr(ti_le_money_get_obj, money_key)
                ti_le_money = ti_le_money
                
                if winning_ratio > 0: # thắng
                    if ti_le_money < 0:
                        ti_le_money = 1
                else: # thua
                    if ti_le_money < 0:
                        ti_le_money = abs(ti_le_money)
                    else:
                        ti_le_money = 1
        else:
            ti_le_money = 1      
                      
                    
        winning_amount = winning_ratio * amount * ti_le_money
        return winning_ratio, winning_amount




class Bet(models.Model):
    _name = 'tsbd.bet'
    time = fields.Datetime(default=fields.Datetime.now)
    current_time = fields.Float()
    @api.onchange('time')
    def _oc_time(self):
        current_time = fields.Datetime.from_string(self.time) - fields.Datetime.from_string(self.match_id.time)
        current_time = current_time.seconds/60
        if current_time > 47:
            current_time =current_time - 15
        self.current_time = current_time
    match_id = fields.Many2one('tsbd.match')
    bet_kind = fields.Selection([('handicap1','handicap1'),('handicap2','handicap2'),('over','over'),('under','under'),('exact_score','exact_score')],default = 'handicap1')
   
    score1 = fields.Integer()
    score2 = fields.Integer()
    
    handicap_money1 = fields.Float(default=100,digit=(6,0))
    handicap_money2 = fields.Float(default=100,digit=(6,0))
    handicap = fields.Float()
    
    
    ou_money1 = fields.Float(default=100,digit=(6,0))
    ou_money2 = fields.Float(default=100,digit=(6,0))
    ou = fields.Float()
    
    exact_money = fields.Float(default=10,digit=(6,0))
    bet_score1 = fields.Integer()
    bet_score2 = fields.Integer()
    
    amount = fields.Float(default=3)
    winning_ratio = fields.Float(compute='_compute_winning_ratio',store=True)
    winning_amount = fields.Float(compute='_compute_winning_ratio',store=True)
    predict_id = fields.Many2one('tsbd.predict')
    predict_match_id = fields.Many2one('tsbd.match')
    
    
    
        
    @api.depends('match_id.score1','match_id.score2','handicap','ou','bet_score1','bet_score2')
    def _compute_winning_ratio(self):
        for r in self:
            bet_kind = r.bet_kind
            if bet_kind:
                winning_ratio,winning_amount = handicap_winning_(r,bet_kind)
                r.winning_ratio=winning_ratio
                r.winning_amount=winning_amount