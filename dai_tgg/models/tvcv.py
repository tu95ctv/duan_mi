# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions,tools,_
from unidecode import unidecode
import re
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import logging
import json
# from unidecode import unidecode
from odoo.addons.dai_tgg.mytools import  name_compute,name_khong_dau_compute



def skip_depends_if_not_congviec_decorator(depend_func):
    def wrapper(*args,**kargs):
        self = args[0]
        for r in self:
            if r.loai_record ==u'Công Việc':
                depend_func(r)
    return wrapper
# def viet_tat(string):
#     string = string.strip()
#     ns = re.sub('\s{2,}', ' ', string)
#     ns = re.sub('[^\w ]','', ns,flags = re.UNICODE)
#     slit_name = ns.split(' ')
#     slit_name = filter(lambda w : True if w else False, slit_name)
#     one_char_slit_name = map(lambda w: w[0],slit_name)
#     rs = ''.join(one_char_slit_name).upper()
#     return rs
# rs = viet_tat(string)

class KhongDauModel(models.Model):
    _name = 'khongdaumodel'
    _auto = False
    name = fields.Char()
    name_khong_dau = fields.Char(compute='name_khong_dau_', store=True)
    name_viet_tat =  fields.Char(compute='name_khong_dau_', store=True)
    @api.depends('name')
    def name_khong_dau_(self):
        name_khong_dau_compute(self)
        
class TVCV(models.Model):
    _name = 'tvcv'

    _parent_name = 'parent_id'
    _inherit = ['khongdaumodel', 'mail.thread']
    _auto = True
    
    
    department_id = fields.Many2one('hr.department',ondelete='restrict', string=u'Đài')
    name = fields.Char(string=u'Tên công việc',required=True)
    loai_record = fields.Selection([(u'Công Việc',u'Công Việc'),(u'Sự Cố',u'Sự Cố'),(u'Sự Vụ',u'Sự Vụ'),(u'Comment',u'Comment')], string = u'Loại Record')
    code = fields.Char(string=u'Mã công việc')
    don_vi = fields.Many2one('donvi',string=u'Đơn vị tính')
    
    do_phuc_tap = fields.Integer(string=u'Độ Phức Tạp')
    thoi_gian_hoan_thanh = fields.Integer(string=u'Thời Gian Hoàn Thành')
    diem = fields.Float(digits=(6, 2),string=u'Điểm',implied_group='base.group_erp_manager', track_visibility='onchange')
    
    @api.onchange('do_phuc_tap','thoi_gian_hoan_thanh')
    def  to_diem_oc_(self):
        if  self.do_phuc_tap and self.thoi_gian_hoan_thanh:
            self.diem = self.do_phuc_tap*self.thoi_gian_hoan_thanh/60 

        
    
    dot_xuat_hay_dinh_ky = fields.Many2one('dotxuathaydinhky',string=u'Đột xuất hay định kỳ')
    cong_viec_cate_id = fields.Many2one('tvcvcate',string=u'Phân loại TVCV')
    diem_percent = fields.Integer(string=u'Phần trăm điểm so với TVCV cha')
    children_ids = fields.One2many('tvcv','parent_id',string=u'Các TVCV Giai Đoạn Con')
    parent_id = fields.Many2one('tvcv',string=u'TVCV Giai Đoạn Cha')
    ghi_chu = fields.Text(u'Ghi Chú')
    active = fields.Boolean(default=True,)
    state = fields.Selection([('draft',u'Bản Nháp'),('confirmed',u'Xác Nhận')],default='draft', string=u'Trạng thái')
    is_bc =  fields.Boolean(u'Có báo cáo',default=True)
   
    is_has_children = fields.Boolean(string=u'Có TVCV Giai Đoạn Con',compute='is_has_children_',store=True)
    co_cong_viec_cha = fields.Boolean(string=u'Có TVCV Giai Đoạn Cha',compute='co_cong_viec_cha_',store=True)
    valid_thu_vien = fields.Boolean(compute='valid_thu_vien_',store=True,string=u'Valid thư viện')

#         
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(TVCV, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        loai_record = self._context.get('default_loai_record')
        if view_type in ['tree','form']:
            loai_record = self._context.get('default_loai_record')
            if loai_record in [u'Sự Cố',u'Sự Vụ',u'Comment']:
                fields = res.get('fields')
                fields['name']['string'] =u'Tên Loại ' + loai_record
            elif loai_record == u'Công Việc':
                fields = res.get('fields')
                fields['name']['string'] =u'Tên TVCV'
        return res
    

    @api.constrains('diem')
    @skip_depends_if_not_congviec_decorator
    def parent_diem_change_children_diem(self):
        for r in self:
            if r.children_ids:
                for child in r.children_ids:
                    ##print '**parent_diem_change_children_diem child.id ** ',child.id
                    child.diem =  child.diem_percent * r.diem/100
                r.children_ids = r.children_ids.ids
    @api.constrains('diem_percent','parent_id')
    @skip_depends_if_not_congviec_decorator
    def children_diem_depend_on_diem_percent(self):
        for r in self:
            if r.parent_id:
                if  r.diem_percent > 100:
                    raise UserWarning(u'Phần Trăm Điểm Không thể lớn hơn 100')
                ##print 'contrains'
                r.diem = r.diem_percent * r.parent_id.diem/100
                ##print 'contrains r.diem = r.diem_percent * r.parent_id.diem/100.0',r.diem,r.diem_percent,r.parent_id.diem/100.0
    @api.model
    def create(self, vals):
        cv = super(TVCV, self).create(vals)
        return cv
    @api.multi
    def write(self, vals):
        res = super(TVCV, self).write(vals)
        return res  
#     def test_common(self):
#         ##print 'self._context',self._context
    def cha_con_valid(self,cha_object):
            diem_con  = sum(cha_object.children_ids.mapped('diem'))
            diem_cha = cha_object.diem
            if cha_object.diem==0:
                return False
            else:
                if abs(diem_cha - diem_con) <0.005*len(cha_object.children_ids) :
                    return True
                else:
                    return False
    @api.depends('diem',
                        'children_ids',#for parent, thay đổi bất cứ gì trong children_ids
                        'parent_id.diem',
                 )     
    @skip_depends_if_not_congviec_decorator
    def valid_thu_vien_(self):
        for r in self:
            if r.children_ids:
                r.valid_thu_vien  = self.cha_con_valid(r)
            elif r.parent_id:
                cha_object = r.parent_id
                r.valid_thu_vien  = self.cha_con_valid(cha_object)
            else:
                r.valid_thu_vien = True
            ##print 'valid tv ',r.id
    @api.depends('parent_id')
    @skip_depends_if_not_congviec_decorator
    def co_cong_viec_cha_(self):
        for r in self:
            if r.parent_id:
                r.co_cong_viec_cha = True
            else:
                r.co_cong_viec_cha = False
                
    @api.constrains('name','parent_id')
    @skip_depends_if_not_congviec_decorator
    def _check_unique_name_per_prid(self):
        for r in self:
            if r.parent_id.id:
                rs = self.search([('name','=',r.name),('parent_id','=',r.parent_id.id)])
                if len(rs)>1:
                    raise ValidationError(u'không được trùng tên trên mỗi parent_id')
    
    @api.depends('children_ids')
    @skip_depends_if_not_congviec_decorator
    
    
    def is_has_children_(self):
        for r in self:
            r.is_has_children = bool(r.children_ids)
    @api.constrains('parent_id')
    @skip_depends_if_not_congviec_decorator
    def _check_category_recursion_check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True
    @api.multi
    def name_get(self,from_name_search=False):
        def get_names(cat):
            res = []
            if cat.name != False:
                while cat:
                        res.append(cat.name)
                        cat = cat.parent_id
            return res
        res = []
        for  r in self:
            name = ' / '.join(reversed(get_names(r)))    
            
            if r.loai_record ==u'Công Việc':
            
#             if from_name_search ==False:
#                 adict=[
# #                                                                 ('id',{'pr':u'TVCV id'}),
#                                                                 ('code',{}),#'pr':u'Mã'
#                                                                 ('name',{'func': lambda x:name}),
# #                                                                 ('diem',{'pr':u'Điểm'}),
# #                                                                 ('don_vi',{'pr':u'Đơn Vị','func':lambda r: r.name}),
#                                                                #('do_phuc_tap',{'pr':u'Độ Phức Tạp'})
#                                                                ]
#             else:
                adict=[
                                                                    ('code',{}),
                                                                    ('name',{'func': lambda x:name}),
                                                                    ('diem',{'pr':u'Điểm','func': lambda val,r: u'%s/%s/%s'%(r.do_phuc_tap,r.thoi_gian_hoan_thanh,val),'karg':{'r':r}}),
    #                                                                 ('don_vi',{'pr':u'Đơn Vị','func':lambda r: r.name}),
                                                                   ]
                name = name_compute(r,adict)
            res.append((r.id,name))
        return res
    
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
# #         raise ValueError('dfasdfd')
#         ##print 'in name_search self.context'*100,self._context
#         res =  super(TVCV,self).name_search( name, args=None, operator='ilike', limit=100)
#         return res
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        all_loai_record = self._context.get('loai_record_more',[])
        default_loai_record = self._context.get('default_loai_record')
        if default_loai_record:
            all_loai_record.append(default_loai_record)
        if u'Công Việc' not in all_loai_record:
            print ('***args in name_search tvcv',args)
            return super(TVCV,self).name_search(name, args=args, operator=operator, limit=limit)
        
        limit=500
        try:
            id_int = int(name)
            ma_tvcv_domain = ['|',('code','ilike',name),('id','=',id_int)]
        except:
            ma_tvcv_domain = [('code','ilike',name)]
        ma_tvcv_domain = expression.OR([['|',('name_khong_dau', 'ilike', name),('name_viet_tat', 'ilike', name)], ma_tvcv_domain])
        thu_vien_id_of_gd_parent_id = self._context.get('thu_vien_id_of_gd_parent_id')
        #print "bool(self._context.get('you_at_gd_form'))",bool(self._context.get('you_at_gd_form'))
        
        if thu_vien_id_of_gd_parent_id and self._context.get('you_at_gd_form'):#self._context.get('you_search_at_gd_form'):
            thu_vien_da_chon_list_txt = self._context.get('thu_vien_da_chon_list')
            if thu_vien_da_chon_list_txt==False:
                thu_vien_da_chon_list = []
            else:
                thu_vien_da_chon_list = json.loads(thu_vien_da_chon_list_txt)
#             thu_vien_id_of_gd_parent_id = self._context.get('thu_vien_id_of_gd_parent_id')
            gd_children_or_not_gd_children_domain = [('id','!=',thu_vien_da_chon_list),'|',('parent_id', '=',thu_vien_id_of_gd_parent_id),('id', '=',self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)]
        else:
            gd_children_or_not_gd_children_domain = [('parent_id','=',False),('id','!=',self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)]
      
        
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            #child = parents.pop()
            child =parents[0]
            parents = parents[1:]
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
#             if ma_tvcv_domain:
#                 last_domain =  expression.OR([expression.AND([domain, args]),ma_tvcv_domain])
#             else:
#                 last_domain =  expression.AND([domain, args])
            
            name_or_code_domain = expression.OR([domain, ma_tvcv_domain])
            last_domain  =  expression.AND([name_or_code_domain, gd_children_or_not_gd_children_domain,args]) 
#             categories = self.search(last_domain, limit=limit)
        else:
            last_domain  =  expression.AND([gd_children_or_not_gd_children_domain,args]) 
        categories = self.search(last_domain, limit=limit)
        
        return categories.name_get(from_name_search=True)    
  
class DonVi(models.Model):
    _name = 'donvi'
    name = fields.Char(required=True)
    tvcv_ids = fields.One2many('tvcv','don_vi')
class DotXuatHayDinhKy(models.Model):
    _name = 'dotxuathaydinhky'
    name = fields.Char(required=True)
    tvcv_ids = fields.One2many('tvcv','dot_xuat_hay_dinh_ky')
class tvcvCate(models.Model):
    _name = 'tvcvcate'
    name = fields.Char(required=True)
    tvcv_ids = fields.One2many('tvcv','cong_viec_cate_id')  
