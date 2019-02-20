# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.osv import expression
from odoo.osv.query import Query
import datetime
from odoo.addons.dai_tgg.mytools import  convert_utc_to_gmt_7
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import os,sys,inspect
# from odoo.addons.dai_tgg.controllers.controllers import download_cvi
# def download_cvi(a):
#     pass
class DLCV(models.TransientModel):
    _name = 'dlcv'
    ngay_bat_dau_filter = fields.Date(string=u'Ngày Bắt Đầu')
    ngay_ket_thuc_filter = fields.Date(string=u'Ngày Kết Thúc')
    is_show_diem_nhan_vien = fields.Boolean(string=u'Có show cột điểm nhân viên không?')
    chon_thang = fields.Selection([(u'Tháng Trước',u'Tháng Trước'),(u'Tháng Này',u'Tháng Này')],string = u'Chọn tháng')
    department_ids = fields.Many2many('hr.department')

    @api.multi
    def download_cvi_binh(self):
        pass
#         download_cvi(self)
#         workbook = download_cvi(self)
#         currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#         dir_tmp = os.path.dirname(currentdir) + '/static/'
#         
#         workbook.save(dir_tmp + 'abc.xls')
#         return {
#             'type' : 'ir.actions.act_url',
#             'url': '/dai_tgg/static/%s' % ('abc.xls'),
#             'target': 'blank',
#         }
#         
        
    def check_department_(self):   
        if not self.department_ids:
                self.department_ids = [self.env.user.department_id.id]
        else:
            if len(self.department_ids) > 1:
                    raise UserError(u'Bạn chỉ được chọn 1 đơn vị download')
            else:
                if not self.user_has_groups('base.group_erp_manager'):
                    select_department_id = self.department_ids[0].id
                    user_department_id = self.env.user.department_id.id
                    child_department_of_user_ids = self.env['hr.department'].search([('id','child_of',user_department_id)]).ids
                    if select_department_id not in child_department_of_user_ids :
                        raise UserError(u'Đơn vị bạn chọn phải cùng  hoặc là con với đơn vị của bạn')
    @api.multi
    def download_cvi_o(self):
        self.check_department_()
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_cvi?model=dlcv&id=%s&more=abc'%(self.id),
             'target': 'new',
        }
    @api.multi
    def download_cvi_by_userlist(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_cvi_by_userlist?model=dlcv&id=%s&more=abc'%(self.id),
             'target': 'new',
        }
        
        
        
    def cvi_filter(self):
        sql_cmd = '''select cvi.user_id,sum(diemtc),u.login,p.name from cvi inner join res_users as u on cvi.user_id = u.id inner join res_partner as p on u.partner_id = p.id group by cvi.user_id ,u.login,p.name'''
        self.env.cr.execute(sql_cmd)
        rsul = self.env.cr.fetchall()
        self.log = rsul
        
# #         utc_time =  datetime.datetime(2018, 1, 11, 20, 0)#datetime.datetime.now()
#         utc_time = datetime.datetime.now()
#         vn_time = convert_utc_to_gmt_7(utc_time)
#         utc_date = utc_time.strftime('%Y-%m-%d')
#        
#         vn_dau_thang_date_begin = vn_time.strftime('%Y-%m-01')
#         vn_time_offset_thang_sau =  vn_time + relativedelta(months=1)
#         vn_dau_thang_sau_date_end = vn_time_offset_thang_sau.strftime('%Y-%m-01')
#         
#         thang_truoc_date_end = vn_time.strftime('%Y-%m-01')
#         thang_truoc_time_begin = vn_time + relativedelta(months=-1)
#         thang_truoc_date_begin = thang_truoc_time_begin.strftime('%Y-%m-01')
#         
#         self.log  = self.env['cvi'].search([('ngay_bat_dau','<=',utc_date)])
#         
#         log2 = u''
#         log2 += u'thang_truoc_date_begin: %s\n'%thang_truoc_date_begin
#         log2 += u'thang_truoc_date_end: %s\n'%thang_truoc_date_end
#         
#         
#         log2 += u'vn_dau_thang_date_begin: %s\n'%vn_dau_thang_date_begin
#         log2 += u'vn_dau_thang_sau_date_end: %s\n'%vn_dau_thang_sau_date_end
#         
#         log2 += u'utc date: %s\n'%utc_date
#         log2 += u'vn date: %s\n'%vn_time.strftime('%Y-%m-%d')
#         log2 += u'utc_time: %s\n'%utc_time
#         log2 += u'vn_time %s\n'%vn_time
#         self.log2 = log2
# #         str_dau_thang = vn_time.strftime('%D')
# #         str_cuoi_thang
# 
#         
# #         self.gio_utc = utc_time
# #         self.gio_vn = vn_time
# #         self.log = utc_time
# #         self.log2 = vn_time
# #         log = u''
# #         fields = self.env['cvi']._fields
# #         for k,v in fields.iteritems():
# #             break
# #         v.string
# #         log += u'string: %s\n type %s'%(v.string,v.type)
# #         self.log = log
# #         return True
#         
# #         args = [('loai_record','=',u'Công Việc')]
# #         self._cr.execute(_sql)
# #         kq_fetch =  self._cr.fetchall()
# #         if self.ngay_bat_dau_filter:
# #             '''SELECT "cvi".id FROM "cvi" WHERE (("cvi"."ngay_bat_dau" >= '2018-01-08 00:00:00')  AND  ("cvi"."loai_record" = 'Công Việc')) ORDER BY "cvi"."id" DESC '''
# #             domain = [('loai_record','=',u'Công Việc')]
# #             domain = expression.AND([[('ngay_bat_dau','>=',fields.Datetime.from_string(self.ngay_bat_dau_filter))],domain])
# #         args = [('department_id.name','ilike',u'ltk'),('loai_record','=',u'Công Việc')]
# #         domain = args
# # #         rs = self.env['cvi'].search(args)
# # #         self.rs_cvi_ids = rs
# # #         log = u''
# # #         _sql = ''' select sum(diemtc) from cvi '''
# # #         self._cr.execute(_sql)
# # #         kq_fetch =  self._cr.dictfetchall()
# # #         log +=u'%s'%kq_fetch
# # #         self.log = log
# # #         log = u''
# # #         if domain:
# # #             e = expression.expression(domain, self.env['cvi'])
# # #             log +='%s\n'%e
# # #             tables = e.get_tables()
# # #             log +='tables : %s\n'%tables
# # #             where_clause, where_params = e.to_sql()
# # #             log +='where_clause %s, where_params %s\n'%(where_clause, where_params)
# # #             where_clause = [where_clause] if where_clause else []
# # #         else:
# # #             where_clause, where_params, tables = [], [], ['"%s"' % self._table]
# # #         query =  Query(tables, where_clause, where_params)
# # #         log +='query : %s\n'%query
# # #         
# # #         order_by = self._generate_order_by(None, query)
# # #         log +='order_by : %s\n'%order_by
# # #         from_clause, where_clause, where_clause_params = query.get_sql()
# # #         log +='from_clause: %s, where_clause: %s, where_clause_params: %s\n'%(from_clause, where_clause, where_clause_params)
# # #         self.log = log
# #         log2 = u''
# #         log=u''
# #         log3=u''
# #         if domain:
# #             e = expression.expression(domain, self.env['cvi'])
# #             leafs= map(lambda leaf: leaf.leaf,e.result)
# #             log3 += '%s\n'%leafs
# #             log +='%s\n'%e
# #             tables = e.get_tables()
# #             log +='tables : %s\n'%tables
# #             where_clause, where_params = e.to_sql()
# #             log +='where_clause %s, where_params %s\n'%(where_clause, where_params)
# #             where_clause = [where_clause] if where_clause else []
# #         else:
# #             where_clause, where_params, tables = [], [], ['"%s"' % self._table]
# #         query =  Query(tables, where_clause, where_params)
# #         log +='query:%s\n'%query
# #         query = self.env['cvi']._where_calc(args)
# #         log2 +='query:%s\n'%query
# # #         self._apply_ir_rules(query, 'read')
# # #         order_by = self._generate_order_by(order, query)
# # 
# #         
# #         from_clause, where_clause, where_clause_params = query.get_sql()
# #         log2 +='from_clause: %s, where_clause: %s, where_clause_params: %s\n' %(from_clause, where_clause, where_clause_params)
# #         where_str = where_clause and (" WHERE %s" % where_clause) or ''
# #         query_str = 'SELECT %s.id FROM '%from_clause + from_clause + where_str
# #         self._cr.execute(query_str, where_clause_params)
# #         rs = self._cr.fetchall()
# # #         res = self._cr.dictfetchall()
# #         self.log = log
# #         self.log2 = log3
        