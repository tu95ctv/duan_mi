# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.tool import  request_html
# from odoo.addons.tsbd.models.leech import  detail_match
from odoo.addons.tsbd.models.tool import   get_or_create_object_sosanh

from bs4 import BeautifulSoup

class Period(models.Model):  
    _name = 'tsbd.period' 
    name = fields.Char()
#     cate_id = fields.Many2one('tsbd.cate')
class Cate(models.Model):  
    _name = 'tsbd.cate' 
    name = fields.Char()
    cate_id = fields.Many2one('tsbd.cate')
    match_ids = fields.One2many('tsbd.match', 'cate_id')
    bang_match_ids = fields.One2many('tsbd.match', 'bang_id')
    cate_ids = fields.One2many('tsbd.bxh','cate_id')
    @api.multi
    def clear_bxh(self):
        self.cate_ids = [(6,0,[])]
    @api.multi
    def trig(self):
        matchs= self.env['tsbd.match'].search([])
        matchs.write({'trig':True})
#     @api.multi
#     def bxh(self):
#         if u'ảng' not in self.name:
#             cate_id = 'cate_id'
#         else:
#             cate_id = 'bang_id'
#         domain = [(cate_id,'=', self.id),('state','!=', u'Chưa bắt đầu')]
#         match_ids = self.env['tsbd.match'].search(domain)
#         home_teams = match_ids.mapped('team1.id')
#         away_teams = match_ids.mapped('team2.id')
#         cate_teams = home_teams + away_teams
#         
#         
#         rt_home_goal = {}
#         read_group_rs = self.env['tsbd.match'].read_group(domain,['team1','score1', 'score2'],['team1'], lazy=False)
#         for ateam in read_group_rs:
#             ateams = {}
#             ateams['home_match_number'] = ateam['__count']
#             ateams['score1'] = ateam['score1']
#             ateams['score2'] = ateam['score2']
#             rt_home_goal[ateam['team1'][0]] = ateams
#         rt_away_goal = {}
#         read_group_rs = self.env['tsbd.match'].read_group(domain,['team2','score1', 'score2'],['team2'], lazy=False)
#         for ateam in read_group_rs:
#             ateams = {}
#             ateams['away_match_number'] = ateam['__count']
#             ateams['score1'] = ateam['score1']
#             ateams['score2'] = ateam['score2']
#             rt_away_goal[ateam['team2'][0]] = ateams
#         rt_home_win= {}
#         read_group_rs = self.env['tsbd.match'].read_group(domain, ['team1','winner','score1', 'score2'],['team1', 'winner'], lazy=False)
#         for ateam in read_group_rs:
#             if ateam['team1'] == ateam['winner']:
#                 ateams = {}
#                 ateams['home_win_count'] = ateam['__count']
#                 rt_home_win[ateam['team1'][0]] = ateams
# 
#         rt_away_win= {}
#         read_group_rs = self.env['tsbd.match'].read_group([(( cate_id ,'=', self.id)),('state','!=', u'Chưa bắt đầu')],['team2','winner','score1', 'score2'],['team2', 'winner'], lazy=False)
#         for ateam in read_group_rs:
#             if ateam['team2'] == ateam['winner']:
#                 ateams = {}
#                 ateams['away_win_count'] = ateam['__count']
#                 rt_away_win[ateam['team2'][0]] = ateams
#         #san nhà
#         rt_home_draw = {}
#         read_group_rs = self.env['tsbd.match'].read_group(domain + [('winner','=', False),('loser','=', False)],['team1','score1', 'score2'],['team1'], lazy=False)
#         for ateam in read_group_rs:
#             ateams = {}
#             ateams['home_draw_count'] = ateam['__count']
#             rt_home_draw[ateam['team1'][0]] = ateams
#         #san khach
#         rt_away_draw = {}
#         read_group_rs = self.env['tsbd.match'].read_group(domain + [('winner','=', False),('loser','=', False)],['team2','score1', 'score2'],['team2'], lazy=False)
#         for ateam in read_group_rs:
#             ateams = {}
#             ateams['away_draw_count'] = ateam['__count']
#             rt_away_draw[ateam['team2'][0]] = ateams
#         for team in cate_teams:
#             new_ateam = {}
#             home_t =  rt_home_win.get(team, {}).get('home_win_count',0)
#             away_t  = rt_away_win.get(team, {}).get('away_win_count',0)
#             home_h = rt_home_draw.get(team, {}).get('home_draw_count',0)
#             away_h =  rt_away_draw.get(team, {}).get('away_draw_count',0)
#             home_tg =  rt_home_goal.get(team, {}).get('score1',0)
#             home_th = rt_home_goal.get(team, {}).get('score2',0)
#             home_match_number =  rt_home_goal.get(team, {}).get('home_match_number',0)
#             away_match_number =  rt_away_goal.get(team, {}).get('away_match_number',0)
#             away_tg = rt_away_goal.get(team, {}).get('score2',0)
#             away_th =  rt_away_goal.get(team, {}).get('score1',0)
#           
#             score_sum = home_tg + away_tg
#             lost_score_sum = home_th + away_th
#             diem = (home_t + away_t ) *3 + (home_h + away_h)
#             hsbt = score_sum - lost_score_sum
#             new_ateam['home_t'] =home_t
#             new_ateam['away_t'] = away_t
#             new_ateam['home_h'] = home_h
#             new_ateam['away_h'] = away_h
#             new_ateam['home_tg'] = home_tg
#             new_ateam['home_th'] =  home_th
#             new_ateam['home_match_number'] = home_match_number
#             new_ateam['away_match_number'] = away_match_number
#             new_ateam['away_tg'] = away_tg
#             new_ateam['away_th'] = away_th
#             
#             new_ateam['cate_id'] = self.id
#             get_or_create_object_sosanh(self,'tsbd.bxh', {'team_id':team}, new_ateam,is_must_update = True)
#         bxh_ids = self.env['tsbd.bxh'].search([('cate_id','=',self.id)])
#         for stt,r in enumerate(bxh_ids) :
#             r.stt = stt +1


    
    def gen_bxh_dict(self, cate_teams, domain):
        rt_home_goal = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['home_match_number'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_home_goal[ateam['team1'][0]] = ateams
        rt_away_goal = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['away_match_number'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_away_goal[ateam['team2'][0]] = ateams
        rt_home_win= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain, ['team1','winner','score1', 'score2'],['team1', 'winner'], lazy=False)
        for ateam in read_group_rs:
#             if ateam['team1'] == ateam['winner']:
            if ateam['winner'] =='team1':
                ateams = {}
                ateams['home_win_count'] = ateam['__count']
                rt_home_win[ateam['team1'][0]] = ateams

        rt_away_win= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team2','winner','score1', 'score2'],['team2', 'winner'], lazy=False)
        for ateam in read_group_rs:
#             if ateam['team2'] == ateam['winner']:
            if ateam['winner'] =='team2':
                ateams = {}
                ateams['away_win_count'] = ateam['__count']
                rt_away_win[ateam['team2'][0]] = ateams
        #san nhà
        rt_home_draw = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain + [('winner','=', False),('loser','=', False)],['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['home_draw_count'] = ateam['__count']
            rt_home_draw[ateam['team1'][0]] = ateams
        #san khach
        rt_away_draw = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain + [('winner','=', False),('loser','=', False)],['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['away_draw_count'] = ateam['__count']
            rt_away_draw[ateam['team2'][0]] = ateams
        bxh_dict = {}
        for team in cate_teams:
            home_t =  rt_home_win.get(team, {}).get('home_win_count',0)
            away_t  = rt_away_win.get(team, {}).get('away_win_count',0)
            home_h = rt_home_draw.get(team, {}).get('home_draw_count',0)
            away_h =  rt_away_draw.get(team, {}).get('away_draw_count',0)
            home_tg =  rt_home_goal.get(team, {}).get('score1',0)
            home_th = rt_home_goal.get(team, {}).get('score2',0)
            home_match_number =  rt_home_goal.get(team, {}).get('home_match_number',0)
            away_match_number =  rt_away_goal.get(team, {}).get('away_match_number',0)
            away_tg = rt_away_goal.get(team, {}).get('score2',0)
            away_th =  rt_away_goal.get(team, {}).get('score1',0)
            score_sum = home_tg + away_tg
            lost_score_sum = home_th + away_th
            diem = (home_t + away_t ) *3 + (home_h + away_h)
            hsbt = score_sum - lost_score_sum
            bxh_dict[team] = {'home_t':home_t, 'away_t': away_t,
                              'home_h': home_h,'away_h':away_h,
                              'home_tg':home_tg,'away_tg':away_tg,
                              'home_th':home_th,'away_th':away_th,
                              'home_match_number':home_match_number, 'away_match_number': away_match_number,
                              'score_sum':score_sum,'lost_score_sum':lost_score_sum,
                              'diem':diem, 'hsbt':hsbt,
                               }
        return bxh_dict
    @api.multi
    def bxh(self):
        if u'ảng' not in self.name:
            cate_id = 'cate_id'
        else:
            cate_id = 'bang_id'
        domain = [(cate_id,'=', self.id),('state','!=', u'Chưa bắt đầu')]
        match_ids = self.env['tsbd.match'].search(domain)
        home_teams = match_ids.mapped('team1.id')
        away_teams = match_ids.mapped('team2.id')
        cate_teams = home_teams + away_teams
        
        
        bxh_dict = self.gen_bxh_dict(cate_teams, domain)
        for team,ateam_bxh_dict in bxh_dict.items():
            new_ateam = {}
            new_ateam['home_t'] =ateam_bxh_dict['home_t']
            new_ateam['away_t'] = ateam_bxh_dict['away_t']
            new_ateam['home_h'] = ateam_bxh_dict['home_h']
            new_ateam['away_h'] = ateam_bxh_dict['away_h']
            new_ateam['home_tg'] = ateam_bxh_dict['home_tg']
            new_ateam['home_th'] =  ateam_bxh_dict['home_th']
       
            new_ateam['away_tg'] = ateam_bxh_dict['away_tg']
            new_ateam['away_th'] = ateam_bxh_dict['away_th']
            new_ateam['home_match_number'] = ateam_bxh_dict['home_match_number']
            new_ateam['away_match_number'] = ateam_bxh_dict['away_match_number']
            new_ateam['cate_id'] = self.id
            get_or_create_object_sosanh(self,'tsbd.bxh', {'team_id':team, 'cate_id':self.id
                                                          }, new_ateam, is_must_update = True)
        
        rg_rs = self.env['tsbd.bxh'].read_group([('cate_id','=', self.id)],['team_id','diem'],['diem'],lazy=False)
        rg_rs =  list(filter(lambda i: i['__count']>1,rg_rs))
        for ateam_rg in rg_rs:
            diem = ateam_rg['diem']
            team_ids = self.env['tsbd.bxh'].search([('diem','=', diem),('cate_id','=',self.id)]).mapped('team_id.id')
            domain = [(cate_id,'=', self.id),('state','!=', u'Chưa bắt đầu'),('team1','in',team_ids),('team2','in',team_ids)]
            doi_dau_bxh_dict = self.gen_bxh_dict(team_ids, domain)
            for team, ex_team_bxh_dict in doi_dau_bxh_dict.items():
                ex_search_dict = {'team_id':team, 'cate_id':self.id}
                ex_update_dict = {'diem_dd':ex_team_bxh_dict['diem']}
                get_or_create_object_sosanh(self,'tsbd.bxh', ex_search_dict,  ex_update_dict, is_must_update = True)
        bxh_ids = self.env['tsbd.bxh'].search([('cate_id','=',self.id)],order='diem desc, diem_dd desc')
        for stt,r in enumerate(bxh_ids) :
            r.stt = stt +1
