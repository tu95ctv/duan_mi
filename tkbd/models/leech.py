# -*- coding: utf-8 -*-
from odoo import models, fields, api
import sys
from time import sleep

VERSION_INFO   = sys.version_info[0]
from odoo import models
# from urllib.request import urlopen
try:
    import urllib.request as url_lib
except:
    import urllib2 as url_lib
from bs4 import BeautifulSoup
def request_html(url):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36' }
    count_fail = 0
    while 1:
        print ('get html',url)
        try:
            if VERSION_INFO == 3:
                req = url_lib.Request(url, None, headers)
                rp= url_lib.urlopen(req)
                mybytes = rp.read()
                html = mybytes.decode("utf8")
            elif VERSION_INFO ==2:
                req = url_lib.Request(url, None, headers)
                html = url_lib.urlopen(req).read()
            return html
        except Exception as e:
            count_fail +=1
            print ('loi khi get html',e)
            sleep(5)
            if count_fail ==5:
                raise ValueError(u'Lỗi get html')
class URL(models.Model):
    _name = 'tkbd.url'
    name = fields.Char()
    

    

class Fetch(models.Model):
    _name = 'tkbd.leech'
    url_id = fields.Many2one('tkbd.url')
    url = fields.Char()
    html = fields.Text()
    test = fields.Text()
    def fetch(self):
        html = request_html(self.url or self.url_id.name)
        self.html = html
    def test_odds(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        ABOdds = soup.select('div#ABOdds')
        self.test = ABOdds[0]
    def test_soup(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        schedule_tables = soup.select('div.schedule_table')
        test = 'len schedule_tables %s'%len(schedule_tables)
        schedule_table_0 = schedule_tables[0]
        trs = schedule_table_0.select('tr')
        test += 'len trs %s'%len(trs)
        for c,tr in enumerate(trs):
            test += 'ROW thứ %s '%c
            for c,td in enumerate(tr.select('td')):  
                test += 'cột  thứ %s '%c +' là:%s '%td.get_text()
                if len(td.select('a')):      
                    href = "http://bongdaso.com/"+td.select('a')[0]['href'].replace("Data=Casting","Data=odds") + '\n'
                    test +=' href: ' + href
            test +='\n'
        self.test = test
        
        
        
        
