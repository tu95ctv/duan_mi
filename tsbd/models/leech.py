# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import  timedelta
from odoo.addons.tsbd.models.tool import  request_html, get_or_create_object_sosanh
from bs4 import BeautifulSoup
from odoo.exceptions import UserError
import re
import datetime
from odoo.addons.tsbd.models.leech_tool import  get_update_dict, get_soup, get_fix_id,GethtmlError
from odoo.addons.tsbd.models.leech_tool import  get_team_date, update_score_odds, getmatchdictlist,get_soup_ajax_link

class Leech(models.Model):
    _name = 'tsbd.leech'
    log = fields.Text()
    log1 = fields.Text()
    parse_log = fields.Text()
    link = fields.Char()
    all_match_link = fields.Char()
    match_ids = fields.Many2many('tsbd.match')
    count = fields.Integer()
    is_get_thong_ke = fields.Boolean()
    all_match_link_select= fields.Selection([('http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1','http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1'),
                                                                ('http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat','http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat mode 2'),
                                                                ('http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1','http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=1&SeasonID=106&CountryRegionID=-1&Period=6',u'Ngoại hạng anh tháng 2'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=3&SeasonID=111&CountryRegionID=-1&Period=5',u'Seria tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=4&SeasonID=110&CountryRegionID=-1&Period=5',u'Laliga tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=5&SeasonID=109&CountryRegionID=-1&Period=5',u'Đức tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=6&SeasonID=108&CountryRegionID=-1&Period=5',u'Pháp tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=2&SeasonID=104&Period=4',u'C1 vòng bảng 17'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=2&SeasonID=112&Period=5',u'C1 vòng bảng 18'),
                                                                ('http://bongdaso.com/AsianCupSchedule.aspx',u'Asian cup'),
                                             
                                             ])
    cate_id = fields.Many2one('tsbd.cate')
    bxh_ids = fields.Many2many('tsbd.bxh','leech_bxh_rel','leech_id', 'bxh_id')
    @api.onchange('all_match_link_select')
    def all_match_link_select_oc_(self):
        self.all_match_link = self.all_match_link_select
    @api.multi
    def clean_match(self):
        for r in self.match_ids :
            r.unlink()
            
    @api.multi
    def leech_all_season(self):
        link = self.all_match_link
        for ss in range (0,7):
            aml = re.sub('Period=\d+','Period=%s'%ss,link)
            self.leech_all_match_function(aml, is_get_thong_ke  =  False)
    @api.multi
    def bxh(self):
        pass
    def leech_all_match(self):
        m_ids = self.with_context({'leech_all_match_function':True}).leech_all_match_function( self.all_match_link, self.count, is_get_thong_ke = self.is_get_thong_ke )
        for m_id in m_ids:
            self.write( {'match_ids': [(4,m_id)]})
    
    @api.multi
    def leech_all_season_auto_get_period(self):
        link = self.all_match_link
        self.leech_all_season_auto_get_period_f(link)
        
        
        
    @api.multi
    def leech_all_season_auto_get_period_f(self,link):
        soup = get_soup(link)
        period = soup.select('div.periods_table td')
        links = []
        for p in period:
            a = p.select('a')
            txt=p.get_text()
            if txt and (u'Vòng loại' not in txt and u'Vòng sơ loại' not in txt ):
                if a:
                    links.append(('http://bongdaso.com/'  + a[0]['href'],txt))
                else:
                    links.append((link,txt))
        for l,t in links:
#             try:
                self.leech_all_match_function(l, is_get_thong_ke  =  False)
#             except ValueError as e:
#                 print (e)
                    
     
 
    
    def leech_a_match(self):
        match_id = self.leeching_a_match_function(self.link)
        self.match_ids = [(4,match_id)]
        
    def leeching_a_match_function(self,match_link, is_write = True, is_get_thong_ke  = True,add_update_dict = {}):
#         search_dict = {}
#         search_list_fields = []
        team_and_begintime,match_date, str_time = get_team_date(self,match_link,add_update_dict)
        search_dict =team_and_begintime
#         if is_write == False:
#             match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, is_create=False, is_write =False)
#             if not match_id:
#                 update_dict, txt_trows = self.get_update_dict (match_link,match_date, is_get_thong_ke =  is_get_thong_ke, add_update_dict = add_update_dict,str_time=str_time)
# #                 raise UserError(u'%s'%search_dict)
#                 match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, update_dict )
#         else:
        update_dict, txt_trows = get_update_dict (self,match_link,match_date, is_get_thong_ke =  is_get_thong_ke, add_update_dict=add_update_dict,str_time = str_time )
        match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, update_dict)
       
        bet_ScoreLines = update_score_odds(self, txt_trows,match_id.id)
        self.log = bet_ScoreLines
        return match_id.id
    
   
    def leech_all_match_function(self, all_match_link, break_count=0, is_write=True,is_get_thong_ke = True, take_match_not_link = True):
        soup = get_soup(all_match_link)
        if '_PlayedMatches' in all_match_link:
            #http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1
            mode = '_PlayedMatches'  #1
        elif 'Data=stat' in all_match_link:
            #http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat
            mode = 'stat' #2
        elif '_ComingMatches' in all_match_link:
        #http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1
            mode = '_ComingMatches' #4
        elif 'AsianCupSchedule' in all_match_link:
            mode = 'AsianCupSchedule'
        else:
            #http://bongdaso.com/LeagueSchedule.aspx?LeagueID=1&SeasonID=106&CountryRegionID=-1&Period=5
            mode = 'SeasonID' #3
            
        match_link_list = getmatchdictlist(self,soup,mode)
        count = 0 
        len_match_ids = len(match_link_list)
        m_ids = []
        for adict in match_link_list:
            add_update_dict = adict#{'cate': adict['cate']}
            print ('***adict ', adict)
            match_link = adict['match_link']
            if not take_match_not_link and  not match_link:
#                 raise UserError(u'akaka')
                continue
            
            try:
                m_id = self.leeching_a_match_function(match_link,is_write = is_write, is_get_thong_ke= is_get_thong_ke, add_update_dict=add_update_dict)
                m_ids.append(m_id)
                
                print ('%s/%s,%s'%(count, len_match_ids, add_update_dict))
            except GethtmlError as e:
                print ('leech a math link but erorr html get url:%s'%e)
                pass
            count+=1
            if break_count and break_count == count:
                break
            
        return m_ids
   
    
    
    
    
    @api.multi
    def trig(self):
        matchs= self.env['tsbd.match'].search([])
        matchs.write({'trig':True})
#         self.match_ids = [(5,0)]
    def test(self):
        template_link = u'http://bongdaso.com/_OddsInfo.aspx?FixtureID=%s&LeagueID=1&SeasonID=50&HomeClubID=14&AwayClubID=15001&HomePrimaryClubID=14&AwayPrimaryClubID=15001&HomeShortCode=NEW&AwayShortCode=WOV&Home=Newcastle&Away=Wolverhampton'
        fix_id = get_fix_id(self.link)
        soup = get_soup_ajax_link(fix_id,template_link)
#         trow_soups = soup.select('div#WHScoreOdd tr')
#         trow_soups = soup.select('div#WHScoreOdd tr')
        trow_soups = soup.select('tr table tr')
        score_odd_lst_strows = []
        print ('len(trow_soups)',len(trow_soups))
        for trow in trow_soups:
            score = trow.select('td')
#             td_odd_down = trow.select('td:nth-of-type(1)')
            if score:
                score = score[0].get_text()
                if ' - ' in score:
                    scores  = score.split(' - ')
                    td2 = trow.select('td:nth-of-type(2)')
                    if td2:
                        td2 = td2[0].get_text()
                        score +=' ' + td2
                    score_odd_lst_strows.append(score)
        txt_trows = u'\n'.join(score_odd_lst_strows)
        self.log = txt_trows
#         fix_id = get_fix_id(self.link)
#         score_and_status_dict = get_score(fix_id)
        
