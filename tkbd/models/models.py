# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Team(models.Model):
    _name = 'tkbd.team'
    name = fields.Char()
def ti_le_char_to_float(ti_le):
    ti_les = ti_le.split(':')
    ti_les = map(honso_char_to_float,ti_les)
    return ti_les
def honso_char_to_float(val):
    vals = val.split(' ')
    vals = sum(map(rational_char_to_float,vals))
    return vals
def rational_char_to_float(val):
    vals = val.split('/')
    if len(vals) ==1:
        val = float(vals[0])
    else:
        val =  float(vals[0])/float(vals[1])
    return val

    
#     chu = fields.Float(digits=(6,3))
#     khach = fields.Float(digits=(6,3))
#     ti_le = fields.Char()
#     ti_le_float_1 = fields.Float(digits=(6,2), compute='ti_le_float_1_',store=True)
#     ti_le_float_2 = fields.Float(digits=(6,2),compute='ti_le_float_1_',store=True)
#     thang_thua_1 =  fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
#     thang_thua_2 =  fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
    
    
    
class Match(models.Model):
    _name = 'tkbd.match'
    name = fields.Char(compute='name_',store=True)
    team_1 = fields.Many2one('tkbd.team')
    team_2 = fields.Many2one('tkbd.team')
    score_1 = fields.Integer()
    score_2 = fields.Integer()
    score_1_current = fields.Integer()
    score_2_current = fields.Integer()
    
    chu = fields.Float(digits=(6,3))
    khach = fields.Float(digits=(6,3))
    ti_le = fields.Char()
    ti_le_float_1 = fields.Float(digits=(6,2), compute='ti_le_float_1_',store=True)
    ti_le_float_2 = fields.Float(digits=(6,2),compute='ti_le_float_1_',store=True)
    thang_thua_1 =  fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
    thang_thua_2 =  fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
    tien_thang_thua_1 = fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
    tien_thang_thua_2 = fields.Float(digits=(6,3),compute='thang_thua_1_2_',store=True)
    
    
    ti_le_tai_xiu_char = fields.Char()
    ti_le_tai_xiu_float = fields.Float(digits=(6,2),compute='ti_le_tai_xiu_float_',store=True)
    tien_an_tai = fields.Float(digits=(6,3))
    tien_an_xiu = fields.Float(digits=(6,3))
    thang_thua_tai =  fields.Float(digits=(6,3),compute='thang_thua_tai_xiu_',store=True)
    thang_thua_xiu =  fields.Float(digits=(6,3),compute='thang_thua_tai_xiu_',store=True)
    
    @api.depends('team_1','team_2','ti_le','ti_le_tai_xiu_char')
    def name_(self):
        for r in self:
            middles = [r.ti_le,r.ti_le_tai_xiu_char]
            middles = filter(lambda val: val !=False,middles)
            middle = u'|'.join(middles)
            names = []
            if r.team_1:
                names.append(r.team_1.name)
            if middle:
                names.append(middle)
            if r.team_2:
                names.append(r.team_2.name) 
            name = u' '.join(names)
            r.name = name
    
    @api.depends('ti_le_tai_xiu_float','score_1','score_2','score_1_current','score_2_current')
    def thang_thua_tai_xiu_(self):
        for r in self:
            delta = (r.score_1 + r.score_2) - (r.ti_le_tai_xiu_float)
            
            if delta ==0:
                ti_le_thang_thua = 0
            elif abs(delta) ==0.25:
                ti_le_thang_thua = 0.5
            else:
                ti_le_thang_thua = 1
            if delta < 0:
                ti_le_thang_thua = 0-ti_le_thang_thua
                
                
            r.thang_thua_tai = ti_le_thang_thua
            r.thang_thua_xiu = 0-ti_le_thang_thua
            
            
    @api.depends('ti_le_tai_xiu_char')
    def ti_le_tai_xiu_float_(self):
        for r in self:
            if r.ti_le_tai_xiu_char:
                r.ti_le_tai_xiu_float = honso_char_to_float(r.ti_le_tai_xiu_char)
    
    
    @api.depends('ti_le')
    def ti_le_float_1_(self):
        for r in self:
            if r.ti_le:
                r.ti_le_float_1,r.ti_le_float_2= ti_le_char_to_float(r.ti_le)
                
    
    @api.depends('ti_le_float_1','ti_le_float_2','score_1','score_2','khach','chu')
    def thang_thua_1_2_(self):
        for r in self:
            delta = (r.score_1 + r.ti_le_float_1 - r.score_1_current) - (r.score_2 + r.ti_le_float_2 - r.score_2_current)
            print('delta',delta,delta==0)
            if delta ==0:
                ti_le_thang_thua = 0
            elif abs(delta) ==0.25:
                ti_le_thang_thua = 0.5
            else:
                ti_le_thang_thua = 1
            if delta < 0:
                ti_le_thang_thua = 0-ti_le_thang_thua
            ti_le_thang_thua_2 = 0-ti_le_thang_thua
            r.thang_thua_1 = ti_le_thang_thua
            r.thang_thua_2 = ti_le_thang_thua_2
            
            if ti_le_thang_thua > 0:#nếu thắng
                if r.chu>0:
                    khach = r.chu
                else:
                    khach = 1
            
            else:#thua
                if r.chu > 0:
                    khach = 1
                else:
                    khach = r.chu
            r.tien_thang_thua_1 = ti_le_thang_thua*khach
            
            if ti_le_thang_thua_2 > 0:#nếu thắng
                if r.khach>0:
                    khach = r.khach
                else:
                    khach = 1
            
            else :#thua
                if r.khach > 0:
                    khach = 1
                else:
                    khach = r.khach
            r.tien_thang_thua_2 = ti_le_thang_thua_2*khach
            
            
                    
                    
                    
            
            
        
class Bet(models.Model):
    _name = 'tkbd.bet'
    _inherit = 'tkbd.match'
    match_id = fields.Many2one('tkbd.match')
    name = fields.Char(compute='name_',store=True)
    team_1 = fields.Many2one('tkbd.team',related='match_id.team_1',store=True)
    team_2 = fields.Many2one('tkbd.team',related='match_id.team_2',store=True)
    score_1 = fields.Integer(related='match_id.score_1',store=True)
    score_2 = fields.Integer(related='match_id.score_2',store=True)
    
    team_id = fields.Many2one('tkbd.team')
    tien_cuoc = fields.Float(digits=(6,2))
    tien_thang_thua = fields.Float(digits=(6,2),compute='tien_thang_thua_',store = True)
    
#     ket_qua_thang_thua_1_2 =  fields.Float(digits=(6,3),compute='ket_qua_thang_thua_1_2_',store=True)   
        
    @api.depends('tien_cuoc','ti_le','team_id','tien_thang_thua_1','tien_thang_thua_2')
    def tien_thang_thua_(self):
        for r in self:
            if r.ti_le and r.team_id:
                if r.team_id == r.team_1:
                    tien_thang_thua_per_one = r.tien_thang_thua_1
                else:
                    tien_thang_thua_per_one = r.tien_thang_thua_2
                r.tien_thang_thua = r.tien_cuoc * tien_thang_thua_per_one
                    
                    
                    
            
    @api.depends('match_id','team_id','ti_le','ti_le_tai_xiu_char')
    def name_(self):
        for r in self:
            rs=['Bet']
            rs.append(r.team_id.name)
            rs.append(r.ti_le)
            rs.append(r.ti_le_tai_xiu_char)
            rs = filter(lambda val: val !=False,rs)
            name = u' | '.join(rs)
            r.name = name
                
#             middles = [r.ti_le,r.ti_le_tai_xiu_char]
#             middles = filter(lambda val: val !=False,middles)
#             middle = u'|'.join(middles)
#             names = []
#             if r.team_1:
#                 names.append(r.team_1.name)
#             if middle:
#                 names.append(middle)
#             if r.team_2:
#                 names.append(r.team_2.name) 
#             name = u' '.join(names)
#             r.name = name
            
        