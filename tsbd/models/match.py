# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.tool import  request_html
# from odoo.addons.tsbd.models.leech import  detail_match
from odoo.addons.tsbd.models.tool import   get_or_create_object_sosanh

from bs4 import BeautifulSoup

from odoo.addons.tsbd.models.bet import handicap_winning_ 

# import re
# from odoo.osv import expression


class Team(models.Model):
    _name='tsbd.team'
    name = fields.Char()
    @api.multi
    def name_get(self):
        rs = []
        for r in self:
            
            stt = self.env['tsbd.bxh'].search([('team_id','=',r.id)])
            if stt:
                stt = stt[0].stt
                name_show = u'%s(%s)'%(r.name,stt)
            else:
                name_show = r.name
            rs.append((r.id,name_show))
        return rs
    
    
    

        
        
class BetScore(models.Model):
    _name ='tsbd.betscore'
    betscore1 = fields.Integer()
    betscore2 = fields.Integer()
    @api.multi
    def name_get(self):
        rs = []
        for r in self:
            name_show = u'%s-%s'%(r.betscore1, r.betscore2)
            rs.append((r.id,name_show))
        return rs
            
        
class BetScoreLine(models.Model):
    _name ='tsbd.betscoreline'
    betscore_id = fields.Many2one('tsbd.betscore')
    match_id = fields.Many2one('tsbd.match')
    odd = fields.Float()
    
    @api.constrains('betscore_id','match_id','odd')
    def scoreline(self):
        for r in self:
            if (r.match_id.score1 == r.betscore_id.betscore1) and  (r.match_id.score2 == r.betscore_id.betscore2):
                r.match_id.score_odd = r.odd
def adecorator(func):
    def awrapper(*arg,**karg):  
        self = arg[0]
        for r in self:
            if r.state != u'Chưa bắt đầu':
                func(r)
    return awrapper
        
sign = lambda x: (-1, 1)[x > 0]
      
class Match(models.Model):
    _name = 'tsbd.match'
    _order = 'date desc'
    
    @api.multi
    def create_match_for_test(self):
        m = self.env['tsbd.match'].create({'team1':1,'score1':False})
        print ('match',m)
        
    @api.multi
    def get_infor_test(self):
        for r in self:
            team_match_limit = r.team_match_limit
            limit = team_match_limit and u'limit %s'%r.team_match_limit or ''
            limit = ''
            team =r.team1.id
            rs = 0
            for number_team in [1,2]:
#                 where =  'team%(team)s = %(team_id)s'
                where =  'team1 = %(team_id)s or team2 = %(team_id)s'%{'team_id':team}
                have =  'having A.team%(team)s= %(team_id)s'%{'team':number_team,'team_id':team}
                sql_query = '''select A.team%(team)s,sum(A.handicap_wl%(team)s) from (select team%(team)s, handicap_wl%(team)s from tsbd_match  where %(where)s %(limit)s) A   group by team%(team)s %(have)s
    '''%{'team':number_team,'team_id':team, 'limit':limit,'where':where,'have':have}
                self.env.cr.execute(sql_query)
                rs2 = self.env.cr.dictfetchall()
#                 rs2 = list(filter(lambda i: i['team%s'%number_team] ==team,rs2))
#                 raise UserError(u'%s'%rs2)
                if rs2:
                    rs2 = rs2[0]['sum']
                    rs +=rs2
        raise UserError(u'%s'%rs)

    
    @api.multi
    def get_infor_test2(self):
#         sql_query = 'select score2,score1,link from tsbd_match where id = 704'
        sql_query = '''select A.team2,sum(A.handicap_wl2) from (select team2, handicap_wl2 from tsbd_match  where team2 = 16) A   group by team2
'''
        self.env.cr.execute(sql_query)
        rs1 = self.env.cr.dictfetchall()
        
        sql_query = '''select A.team1,sum(A.handicap_wl1) from (select team1, handicap_wl1 from tsbd_match  where team1 = 16) A   group by team1
'''
        self.env.cr.execute(sql_query)
        rs2 = self.env.cr.dictfetchall()
        
        raise UserError(u'%s %s'%(rs1,rs2))
            
  
    
        
        
    @api.multi    
    def detail_match_button(self):
        pass
#         search_dict,update_dict = detail_match(self, self.link)
#         search_dict.update(update_dict)
#         self.write(search_dict)
        
    def get_odds_button(self):
        rs= self.get_odds(self.link)
        raise UserError(u'%s'%rs)


    @api.multi
    def leech_button(self):
        rs  = request_html(self.link)
        file = open('/media/sf_C_DRIVE/D4/dl/testfile.html','w') 
        file.write(rs) 
        file.close() 
        self.log =rs
        
    @api.multi
    def parse_button(self):
        pass
#         file = open('/media/sf_C_DRIVE/D4/dl/testfile.html','r') 
#         html = file.read()
#         soup = BeautifulSoup(html, 'html.parser')
#         txt_trows = all_coming_match(soup)
#         self.parse_log =txt_trows
        
        
    log = fields.Text()
    parse_log = fields.Text()
    link = fields.Char()
    trig = fields.Boolean()
    betscoreline_ids = fields.One2many('tsbd.betscoreline', 'match_id')
    def default_time(self):
        if 'leech_all_match_function' in self._context:
            return False
        else:
            return fields.Datetime.now()
    time= fields.Datetime(default= default_time)
    date = fields.Date()
    
    current_time =  fields.Float()
    state = fields.Char()
    cate_id = fields.Many2one('tsbd.cate')
    bang_id = fields.Many2one('tsbd.cate')
    
    period_id = fields.Many2one('tsbd.period')
    name = fields.Char(compute='name_',store=True)
    @api.depends('team1','team2','time','score1','score2')
    def name_(self):
        for r in self:
            try:
                time_txt = fields.Datetime.from_string(r.time).strftime('%d/%m/%Y %H:%M')
                name = r.team1.name + '    ' + str(r.score1) +' - ' + str(r.score2) + '    ' + r.team2.name + '    ' + time_txt
                r.name = name
            except:
                pass
    match_link = fields.Char()
    score_odd = fields.Float()
    team1= fields.Many2one('tsbd.team')
    team2= fields.Many2one('tsbd.team')
    score1 = fields.Integer(default=False)
    score2 = fields.Integer()
    event_ids =  fields.One2many('tsbd.event','match_id')
    bet_ids =  fields.One2many('tsbd.bet','match_id')
    
    begin_handicap_money1 =  fields.Float(default=100,digit=(6,3))
    begin_handicap_money2 =  fields.Float(default=100,digit=(6,3))
    begin_handicap =  fields.Float(digit=(6,2))
    
    begin_ou_money1 =  fields.Float(default=100,digit=(6,3))
    begin_ou_money2 =  fields.Float(default=100,digit=(6,3))
    begin_ou =  fields.Float(digit=(6,2))
    
    curent_handicap_money1 =  fields.Float(default=100,digit=(6,3))
    curent_handicap_money2 =  fields.Float(default=100,digit=(6,3))
    curent_handicap = fields.Float(digit=(6,2))
    
    curent_ou_money1 =  fields.Float(default=100,digit=(6,3))
    curent_ou_money2 =  fields.Float(default=100,digit=(6,3))
    curent_ou =  fields.Float(digit=(6,2))
    
    predict_ids = fields.One2many('tsbd.predict','match_id')
    total_winning_amount = fields.Float(compute='total_winning_amount_',store=True)
    @api.depends('bet_ids')
    def total_winning_amount_(self):
        for r in self:
            r.total_winning_amount = sum(r.bet_ids.mapped('winning_amount'))
    

    winner = fields.Selection([('doi_nha',u'Đội nhà'), ('doi_khach',u'Đội khách'), ('hoa',u'Hai đội hòa')], compute='_match_winner', store= True)
    loser = fields.Selection([('doi_nha',u'Đội nhà'), ('doi_khach',u'Đội khách'), ('hoa',u'Hai đội hòa')], compute='_match_winner', store= True)
    @api.depends('score1','score2','trig')
    @adecorator
    def _match_winner(self):
        for r in self:
            if r.score1 > r.score2:
                r.winner = 'doi_nha'
                r.loser = 'doi_khach'
            elif r.score1< r.score2:
                r.winner = 'doi_khach'
                r.loser = 'doi_nha'    
            else:
                r.winner = 'hoa'
                r.loser = 'hoa'    
    # compute fields 
    keo_0_025_05 = fields.Float(compute='_keo_0_025_05', store=True)
    @api.depends('score1', 'score2', 'begin_handicap','state','trig')
    def _keo_0_025_05(self):
        for r in self:
            r.keo_0_025_05 = abs(r.begin_handicap - float(int(r.begin_handicap)))
    
    handicap_0_05_1 = fields.Float(compute='handicap_wl_compute_', store=True)
    
    cua_tren_hay_cua_duoi = fields.Selection([(u'cua_tren',u'Cửa trên'), (u'cua_duoi',u'Cửa dưới'), (u'hoa_tien',u'Hòa tiền'), (u'team1',u'team1'), (u'team2',u'team2')], 
                                       compute='handicap_wl_compute_', store=True)
    handicap_bet_winner = fields.Selection([('team1',u'Team1'), ('team2',u'Team 2'), ('hoa',u'Hòa')], compute='handicap_wl_compute_', store= True)
    handicap_bet_loser = fields.Selection([('team1',u'Team1'), ('team2',u'Team 2'), ('hoa',u'Hòa')], compute='handicap_wl_compute_', store= True)
    handicap_wl1 = fields.Float(compute='handicap_wl_compute_', store=True)
    handicap_wl2 = fields.Float(compute='handicap_wl_compute_', store=True)
    handicap_win_amount = fields.Float(compute='handicap_wl_compute_', store=True)
    handicap_lost_amount = fields.Float(compute='handicap_wl_compute_', store=True)
    handicap_wl_amount1 = fields.Float(compute='handicap_wl_compute_', store=True)
    handicap_wl_amount2 = fields.Float(compute='handicap_wl_compute_', store=True)
    
    @api.depends('score1', 'score2', 'begin_handicap','state', 'trig')
    @adecorator
    def handicap_wl_compute_(self):
        for r in self:
            if r.state != u'Chưa bắt đầu':
                ratio, amount = handicap_winning_(None, bet_kind='handicap1',mode='predict', match_id =r)
                r.handicap_wl1 = ratio
                r.handicap_wl2 = -ratio
                r.handicap_0_05_1 = abs(ratio)
                if ratio > 0:
                    doi_thang = 'team1'
                    r.handicap_bet_winner ='team1'
                    r.handicap_bet_loser = 'team2'
                    r.handicap_win_amount = amount
                    ratio_handicap_lost, handicap_lost_amount = handicap_winning_(None, bet_kind='handicap2',mode='predict', match_id =r)
                    r.handicap_lost_amount = handicap_lost_amount
                    r.handicap_wl_amount1 = amount
                    r.handicap_wl_amount2 = handicap_lost_amount
                elif ratio < 0:
                    doi_thang = 'team2'
                    r.handicap_bet_winner = 'team2'
                    r.handicap_bet_loser = 'team1'
                    ratio_handicap_win, handicap_win_amount = handicap_winning_(None, bet_kind='handicap2', mode='predict', match_id =r)
                    r.handicap_lost_amount = amount
                    r.handicap_win_amount = handicap_win_amount
                    r.handicap_wl_amount1 = amount
                    r.handicap_wl_amount2 = handicap_win_amount
                else:
                    doi_thang= 'hoa_tien'
                    r.handicap_bet_winner = 'hoa'
                    r.handicap_bet_loser = 'hoa'
                adict  ={}
                if r.begin_handicap > 0:
                    adict = {'team1':'cua_tren', 'team2':'cua_duoi'}
                elif r.begin_handicap < 0:
                    adict = {'team2':'cua_tren', 'team1':'cua_duoi'}
                rs = adict.get(doi_thang, doi_thang)
                r.cua_tren_hay_cua_duoi = rs       
    context_team_handicap_wl = fields.Float(compute='context_team_handicap_wl_')
    @api.depends('team1','team2','handicap_wl1','handicap_wl2')
    @adecorator
    def context_team_handicap_wl_(self):
        team = self._context.get('team')
        if team:
            for r in self:
                if r.team1.id == team:
                    r.context_team_handicap_wl = r.handicap_wl1
                elif r.team2.id == team:
                    r.context_team_handicap_wl = r.handicap_wl2
    sum_handicap_wl1 = fields.Float(compute='sum_handicap_wl1_2_')
    sum_handicap_wl2 = fields.Float(compute='sum_handicap_wl1_2_')
    @api.depends('team1', 'team2','team_match_limit','handicap_wl1','handicap_wl2','team_match_limit')
    def sum_handicap_wl1_2_(self):
        for r in self:
            team_match_limit = r.team_match_limit
            limit = team_match_limit and u'limit %s'%r.team_match_limit or ''
            for f_name in ['1','2']:
#                 team_id =r.team1.id
                team_id =getattr(r,'team%s'%f_name).id
                rs = 0
                for number_team in [1,2]:
    #                 where =  'team%(team)s = %(team_id)s'
                    where =  "(team1 = %(team_id)s or team2 = %(team_id)s) and state = 'Kết thúc' order by date desc"%{'team_id':team_id}
                    have =  'having A.team%(number_team)s= %(team_id)s'%{'number_team':number_team,'team_id':team_id}
                    sql_query = '''select A.team%(number_team)s,sum(A.handicap_wl%(number_team)s) from (select team%(number_team)s, handicap_wl%(number_team)s from tsbd_match  where %(where)s %(limit)s) A   group by team%(number_team)s %(have)s
        '''%{'number_team':number_team,'team_id':team_id, 'limit':limit,'where':where,'have':have}
    #                 raise UserError(u'%s'%sql_query)
                    self.env.cr.execute(sql_query)
                    rs2 = self.env.cr.dictfetchall()
    #                 rs2 = list(filter(lambda i: i['team%s'%number_team] ==team,rs2))
    #                 raise UserError(u'%s'%rs2)
                    if rs2:
                        rs2 = rs2[0]['sum']
                        rs +=rs2
                setattr(r,'sum_handicap_wl%s'%f_name,rs)
                
                
                
                
    over_or_under = fields.Selection([('over','Over'), ('under','Under'),('draw',u'Hòa')], compute='over_or_under_compute_', store=True)
    over_0_05_1 = fields.Float(compute='over_or_under_compute_', store=True)
    over_wl = fields.Float(compute='over_or_under_compute_', store=True)
    under_wl = fields.Float(compute='over_or_under_compute_', store=True)
    over_wl_amount = fields.Float(compute='over_or_under_compute_', store=True)
    under_wl_amount = fields.Float(compute='over_or_under_compute_', store=True)
    ou_win_amount = fields.Float(compute='over_or_under_compute_', store=True)
    ou_lost_amount = fields.Float(compute='over_or_under_compute_', store=True)
    @api.depends('score1','score2','begin_ou','trig')
    @adecorator
    def over_or_under_compute_(self):
        for r in self:
            ratio_over, over_amount = handicap_winning_(None, bet_kind='over',mode='predict', match_id =r)
            r.over_wl = ratio_over
            r.under_wl = -ratio_over
            r.over_0_05_1 = abs(ratio_over)
            if ratio_over > 0:
                r.over_or_under = 'over'
                ratio_under, under_amount = handicap_winning_(None, bet_kind='under',mode='predict', match_id =r)
                r.ou_win_amount = over_amount
                r.ou_lost_amount = under_amount
            elif ratio_over < 0:
                r.over_or_under = 'under'
                ratio_under, under_amount = handicap_winning_(None, bet_kind='under',mode='predict', match_id =r)
                r.ou_win_amount = under_amount
                r.ou_lost_amount = over_amount
            else:
                r.over_or_under = 'draw'
                under_amount = 0
            r.over_wl_amount = over_amount
            r.under_wl_amount = under_amount
            
    
    team1_over = fields.Integer(compute = 'team1_team_2_over_under_')
    team1_under = fields.Integer(compute = 'team1_team_2_over_under_')
    team2_over = fields.Integer(compute = 'team1_team_2_over_under_')
    team2_under = fields.Integer(compute = 'team1_team_2_over_under_')
    @api.depends('team1_match_ids','trig')
    def team1_team_2_over_under_(self):
        for r in self:
            teams =[('team1',r.team1.id), ('team2',r.team2.id)]
            for team_name, team in teams:
                rs1 = self.env['tsbd.match'].read_group(['|', ('team1', '=', team ), ('team2', '=', team )],['over_or_under'], ['over_or_under'], lazy=False )
                for adict in rs1:
                    over_or_under = adict['over_or_under']
                    if over_or_under =='over' or over_or_under =='under':
                        setattr(r, '%s_%s'%(team_name,over_or_under), adict['__count'])
    
    team1_match_ids = fields.Many2many('tsbd.match', 'match_match_rel', 'match_id', 'team1_match_id', compute='team1_match_ids_')
    team_match_limit = fields.Integer()
    @api.depends('team1','team_match_limit')
    def team1_match_ids_(self):
        for r in self:
            rs = self.env['tsbd.match'].search(['|', ('team1', '=', r.team1.id ), ('team2', '=', r.team1.id ),('state','!=',u'Chưa bắt đầu')],limit=r.team_match_limit or None)
            r.team1_match_ids = [(6,0,rs.ids)]
    team2_match_ids = fields.Many2many('tsbd.match', 'match_matchofteam2_rel', 'match_id', 'team2_match_id', compute='team2_match_ids_', )
    @api.depends('team2', 'team_match_limit')
    def team2_match_ids_(self):
        for r in self:
            rs = self.env['tsbd.match'].search(['|', ('team1', '=', r.team2.id ), ('team2', '=', r.team2.id ),('state','!=',u'Chưa bắt đầu')],limit=r.team_match_limit or None)
            r.team2_match_ids = [(6,0,rs.ids)]
            
   
   
    
    is_copy_begin_to_curent = fields.Boolean()
    statictis_match_ids =  fields.Many2many('tsbd.match','match_statictis_match_rel','match_id', 'statictis_match_id')
    
    @api.onchange('current_time')
    def _oc_current_time(self):
        current_time = self.current_time
        current_time = current_time + 15 if current_time > 47 else current_time
        self.time = datetime.now() -  timedelta(minutes=current_time)
        
        
    @api.onchange('is_copy_begin_to_curent')
    def _oc_is_copy_begin_to_curent(self):
        if self.is_copy_begin_to_curent:
            for handicap_or_ou in ['handicap','ou']:
                for field in ['_money1','_money2','']:
                    field_name_get = 'begin_' + handicap_or_ou + field
                    field_name_set = 'curent_' + handicap_or_ou + field
                    setattr(self, field_name_set, getattr(self, field_name_get))
            
    
    @api.onchange('event_ids')
    def _oc_event_ids(self):
        if self.event_ids:
            self.score1=self.event_ids[-1].score1
            self.score2=self.event_ids[-1].score2