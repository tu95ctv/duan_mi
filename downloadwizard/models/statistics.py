# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError
class Statisticslines(models.TransientModel):
    _name = 'downloadwizard.statisticslinestrans'
    location_id = fields.Many2one('stock.location')
    categ_id = fields.Many2one('product.category')
    name_categ =  fields.Char(string=u'Tiêu chí')
    quantity = fields.Integer(string=u'Tổng Số lượng vật tư')
    ket_luan = fields.Char()
    
    
class StatisticslinesI(models.Model):
    _name = 'downloadwizard.statisticslines'
    _inherit =  'downloadwizard.statisticslinestrans'
    statistics_id = fields.Many2one('downloadwizard.statistics')
#     name_categ =  fields.Char(string=u'Tiêu chí')
#     quantity = fields.Integer(string=u'Tổng Số lượng vật tư')



class Statistics(models.Model):
    _name='downloadwizard.statistics'
    model_name= fields.Char()
    date_time = fields.Datetime(default=fields.Datetime.now)
    statistics_ids = fields.One2many('downloadwizard.statisticslines','statistics_id',compute='statistics_ids_',store=True)
#     statistics_ids = fields.Many2many('downloadwizard.statisticslines','statistics_statisticsline_relate','st_id','stl_id',compute='statistics_ids_')
    
    
    def ket_luan_same_name_diff_pn(self,i):
        product_name = i['name']
        pn_domain = [('name','=',product_name)]
        pn_read_group_rs = self.env['product.product'].read_group(pn_domain,['pn'],['pn'],lazy=False)
        pn_read_group_rs_simple = list(map(lambda i: i['pn'],pn_read_group_rs))
        pn_read_group_rs_simple_txt = u'PNs: %s'%pn_read_group_rs_simple
        if i['__count'] != len(pn_read_group_rs_simple):
            raise UserError("i['__count'] != len(pn_read_group_rs_simple)")
        return ( product_name,i['__count'],pn_read_group_rs_simple_txt)
    @api.depends('model_name')
    def statistics_ids_(self):
      
        statistics_ids = []
        slvt = self.env['product.product'].search_count([])
        statistics_ids.append((0,0,{'name_categ':u'slvt','quantity':slvt}))
        # serial mới thay đổi
        recently_time = datetime.now() +timedelta (minutes=-30)
        recently_time =  fields.Datetime.to_string(recently_time)
        domain_recently = [('write_date','>',recently_time)]
        changed_sn_number = self.env['stock.production.lot'].search_count(domain_recently)
        statistics_ids.append((0,0,{'name_categ':u'serial mới thay đổi','quantity':changed_sn_number}))
  
        # vat tu moi thay doi
        changed_pr = self.env['product.product'].search_count(domain_recently)
        statistics_ids.append((0,0,{'name_categ':u'changed_pr','quantity':changed_pr}))
        
        # kho moi thay doi
        domain_changed_stock =  [('location_id.usage','=','internal')]
        domain_changed_stock.extend(domain_recently)
        changed_stock = self.env['stock.quant'].search_count(domain_changed_stock)
        statistics_ids.append((0,0,{'name_categ':u'changed_stock','quantity':changed_stock}))
        
        
        read_group_rs = self.env['product.product'].read_group([],['name'],['name'],lazy=False)
#         statistics_ids.append((0,0,{'name_categ':u'len(read_group_rs)','ket_luan':len(read_group_rs)}))
#         statistics_ids.append((0,0,{'name_categ':u'read_group_rs','ket_luan':read_group_rs}))
        
        slvt_same_name = slvt - len(read_group_rs)
#         statistics_ids.append((0,0,{'name_categ':u'Số lượng vật tư cùng tên khác PN','quantity':slvt_same_name}))
        
        ket_luan_same_name_diff_pn =  list(map(self.ket_luan_same_name_diff_pn,filter(lambda i:i['__count']>1,read_group_rs)))
        statistics_ids.append((0,0,{'name_categ':u'vật tư cùng tên khác partnumber','quantity':slvt_same_name,'ket_luan':ket_luan_same_name_diff_pn}))
        statistics_ids.append((0,0,{'name_categ':u'SL name có nhiều hơn 1 PN','quantity':len(ket_luan_same_name_diff_pn)}))
        
        # số vật tư không có categ all
        so_vat_tu_categ_all = self.env['product.product'].search_count([('categ_id.name','=','All')])
        statistics_ids.append((0,0,{'name_categ':u'so_vat_tu_categ_all','quantity':so_vat_tu_categ_all}))
        
        # số vật tư không có categ Khác
        so_vat_tu_categ_khac = self.env['product.product'].search_count([('categ_id.name','=','Khác')])
        statistics_ids.append((0,0,{'name_categ':u'so_vat_tu_categ_khac','quantity':so_vat_tu_categ_khac}))
        # Số lượng vật tư không có thiết bị
        so_vat_tu_not_hast_thiet_bi = self.env['product.product'].search_count([('thiet_bi_id','=',False)])
        statistics_ids.append((0,0,{'name_categ':u'so_vat_tu_not_hast_thiet_bi','quantity':so_vat_tu_not_hast_thiet_bi}))
        
        # Số lượng vật tư không có HXS
        so_vat_tu_not_hang_sx = self.env['product.product'].search_count([('brand_id','=',False)])
        statistics_ids.append((0,0,{'name_categ':u'so_vat_tu_not_hang_sx','quantity':so_vat_tu_not_hang_sx}))
        
        
        # vật tư không có PN
        vt_not_has_pn = self.env['product.product'].search_count([('pn','=',False)])
        statistics_ids.append((0,0,{'name_categ':u'vt_not_has_pn','quantity':vt_not_has_pn}))
        
        # vật tư không có sn
        vt_not_has_sn = self.env['product.product'].search_count([('tracking','=','none')])
        statistics_ids.append((0,0,{'name_categ':u'vt_not_has_sn','quantity':vt_not_has_sn}))
        
        
        # số lượng loại vật tư có trong trạm LTK
        vt_co_trong_kho_ltk = self.env['stock.quant'].read_group([('location_id.complete_name','like','LTK'),('quantity','>',0)],['product_id'],['product_id'])
        statistics_ids.append((0,0,{'name_categ':u'vt_co_trong_kho_ltk','quantity':len(vt_co_trong_kho_ltk)}))
        
        # số lượng loại vật tư có trong trạm TTI
        vt_co_trong_kho_tti = self.env['stock.quant'].read_group([('location_id.complete_name','like','TTI'),('quantity','>',0)],['product_id'],['product_id'])
        statistics_ids.append((0,0,{'name_categ':u'vt_co_trong_kho_tti','quantity':len(vt_co_trong_kho_tti)}))
        
      
        # sn có ở 2 nơi
        vt_co_trong_kho_tti = self.env['stock.quant'].read_group([('location_id.complete_name','like','TTI'),('quantity','>',0)],['product_id'],['product_id'])
        vt_co_trong_kho_tti_va_ltk  = list(filter(lambda i: self.env['stock.quant'].search([('location_id.complete_name','like','LTK'),('quantity','>',0),('product_id','=',i['product_id'][0])]),vt_co_trong_kho_tti))
        statistics_ids.append((0,0,{'name_categ':u'vt_co_trong_kho_tti_va_ltk','ket_luan':vt_co_trong_kho_tti_va_ltk,'quantity':len(vt_co_trong_kho_tti_va_ltk)}))
        
        
        
        self.statistics_ids = statistics_ids

        


