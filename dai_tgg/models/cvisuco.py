# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import convert_odoo_datetime_to_vn_str,name_compute,convert_odoo_datetime_to_vn_datetime
from unidecode import unidecode
from odoo.exceptions import ValidationError,UserError

class CviSuCo(models.Model):
    
    _name = 'cvisuco'
    _auto = False
    tvcv_id = fields.Many2one('tvcv', string=u'TVCV/ Loại sự cố/ Loại sự vụ',ondelete='restrict')

    is_giao_ca = fields.Boolean(u'Giao ca')
    cvi_id = fields.Many2one('cvi',u'Sự cố/công việc liên quan')
    cvi_cm_ids = fields.One2many('cvi','cvi_id',u'Công việc, comment liên quan')
    nguyen_nhan     = fields.Char(string=u'Nguyên nhân')
    name = fields.Char(compute='name_',store=True)
    noi_dung = fields.Text(string=u'Nội dung')
    noi_dung_khong_dau = fields.Text(string=u'Nội dung không dấu', compute='noi_dung_khong_dau_',)  
#     cvi_id = fields.Many2one('cvi')
#     giao_ca_id = fields.Many2one('ctr',string=u'Ca Trực')
    file_ids = fields.Many2many('dai_tgg.file','cvi_file_relate','cvi_id','file_id',string=u'Files đính kèm')
    doitac_ids = fields.Many2many('res.partner',string=u'Đối Tác')
#     department_id = fields.Many2one('hr.department',string=u'Đơn vị tạo',required=True,readonly=True,default = lambda self:  self.env.user.department_id.id,ondelete='restrict')
    department_id = fields.Many2one('hr.department',string=u'Đơn vị tạo',ondelete='restrict',
                                    default= lambda self:self.env.user.department_id.id,
#                                     compute="department_id_",
#                                     store=True,
                                    copy=False
                                    )
    department_ids = fields.Many2many('hr.department', string=u'Đơn vị liên quan' )
    loai_record = fields.Selection([(u'Công Việc',u'Công Việc'),
                                    (u'Sự Cố',u'Sự Cố'),
                                    (u'Sự Vụ',u'Sự Vụ'),
                                    (u'Comment',u'Comment')
                                    ], string = u'Loại Record',default=u'Công Việc')
    loai_record_show =  fields.Selection([(u'Công Việc',u'Công Việc'),(u'Sự Cố',u'Sự Cố'),(u'Sự Vụ',u'Sự Vụ'),(u'Comment',u'Comment')], string = u'Loại Record',compute='loai_record_show_')
    ngay_bat_dau =  fields.Date(compute='ngay_bat_dau_',store=True,string=u'Ngày')
    gio_bat_dau = fields.Datetime(string=u'Giờ bắt đầu', default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(string=u'Giờ Kết Thúc',default=fields.Datetime.now)
    duration = fields.Float(digits=(6, 1), help='Duration in Hours',compute = '_get_duration', store = True,string=u'Thời lượng (giờ)')
    user_id = fields.Many2one('res.users',default =  lambda self: self.env.uid, readonly=True, string=u'Nhân viên tạo',required=True,copy=False)   
#     ctr_ids  = fields.Many2many('ctr','ctr_cvi_relate','cvi_id','ctr_id',string=u'Ca Trực')
    
    ctr_id  = fields.Many2one('ctr',string=u'Ca Trực',copy=False)
#     ctr_show = fields.Char(compute='ctr_show_',string=u'Số ca trực')
#     comment_ids = fields.One2many('cvi','cvi_id',string=u'Comments')
#     comments_show = fields.Char(compute='comments_show_',string=u'Comments')
    trig_field = fields.Boolean()
    is_bc =  fields.Boolean(u'Có báo cáo',default=True)
     
    @api.onchange('tvcv_id')
    def is_bc_oc(self):
        self.is_bc = self.tvcv_id.is_bc
        
    @api.depends('user_id')
    def department_id_(self):
        for r in self:
            r.department_id = r.user_id.department_id.id
            
    @api.depends('noi_dung')
    def noi_dung_khong_dau_(self):
        for r in self:
            if r.noi_dung:
                r.noi_dung_khong_dau = unidecode(r.noi_dung)
    @api.depends('loai_record')
    def loai_record_show_(self):
        for r in self:
            r.loai_record_show = r.loai_record
            
#     @api.depends('comment_ids')
#     def comments_show_(self):
#         for r in self:
#             comment_ids_text_lists = []
#             for i in r.comment_ids:
#                 i_text = name_compute_char_join_rieng(i, [
#                     ('create_date',{'func':convert_odoo_datetime_to_vn_str}),#,'pr_more':u'('
#                     ('create_uid',{'func': lambda r: r.name ,'join_char':u'-'}),#'sf_more':u')' 
#                     ('noi_dung',{'pr':u'',}),
#                                           ],
#                                        join_char = ' ')
#                 comment_ids_text_lists.append(i_text)
#             r.comments_show = u' | '.join(comment_ids_text_lists)
                
        


            
            
            
#     @api.depends('ctr_ids')
#     def ctr_show_(self):
#         for r in self:
#             r.ctr_show =u'%s ca trực'% len(r.ctr_ids)
 
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(CviSuCo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        fields = res.get('fields')
        if view_type in ['tree','form']:
            default_loai_record = self._context.get('default_loai_record')
            if default_loai_record in [u'Sự Cố',u'Sự Vụ',u'Comment']:
                
                fields['tvcv_id']['string'] =u'Loại ' + default_loai_record 
            elif default_loai_record == u'Công Việc':
                fields = res.get('fields')
                fields['tvcv_id']['string'] =u'Thư Viện Công Việc'
#                 fields['user_id']['string'] =u'Nhân Viên Làm'
        if view_type =='form':
            if self._context.get('you_at_gd_form'):
                context='''{'thu_vien_da_chon_list':parent.get('thu_vien_da_chon_list'), 
                         'you_at_gd_form':context.get('you_at_gd_form'),
                        'loai_record_more':context.get('loai_record_more',[]),
                         'thu_vien_id_of_gd_parent_id':parent.get('tvcv_id'),  
                         'default_loai_record':loai_record,
                         'tree_view_ref':tree_view_ref, 
                         'search_view_ref': search_view_ref ,}'''
            else:

                context='''{
                         'default_loai_record':loai_record,
                         'tree_view_ref':tree_view_ref, 
                         'search_view_ref': search_view_ref ,}'''
                
            fields['tvcv_id']['context'] = context
        return res
    @api.depends('loai_record')
    def tree_view_ref_(self):
        for r in self:
            if r.loai_record ==u'Công Việc':
                r.tree_view_ref = 'dai_tgg.tvcv_list'
                r.search_view_ref = 'dai_tgg.tvcv_search'
            else:
                r.tree_view_ref = 'dai_tgg.loai_suco_suvu_list'
                r.search_view_ref = 'dai_tgg.loai_suco_suvu_search'
                
#     @api.depends('noi_dung')
#     def noi_dung_trich_dan_(self):
#         for r in self:
#             if r.noi_dung:
#                 if len(r.noi_dung) > 30:
#                     r.noi_dung_trich_dan = r.noi_dung[:30] + u'...'
#                 else:
#                     r.noi_dung_trich_dan = r.noi_dung
                
                    
    def get_names(self):
            adict = {u'Công Việc':u'TVCV',u'Sự Cố':u'Loại',u'Sự Vụ':u'Loại',u'Comment':u'Loại'}
            if self.loai_record :
                adict=[
                                              ('id',{'pr':u'%s,id'%self.loai_record}),
                                              ('tvcv_id',{'pr':adict[self.loai_record],'func':lambda val:val.name}),
                                              ('noi_dung',{'pr':u'Nội Dung', 'skip_if_False':False,'func':lambda val: val[0:30]+'...' if  (val and len(val)>30) else  val}),
                                              ]
                if self._context.get('default_loai_record') ==u'Công Việc':
                    adict.append(('user_id',{'func':lambda r:r.name,'pr':u'Người Làm','skip_if_False':False}))
                name  = name_compute(self,adict=adict)
            else:
                name = False
            return name
    @api.multi
    def name_get(self):
        return [(r.id, r.get_names()) for r in self]
    
    @api.depends('tvcv_id','loai_record','noi_dung')
    def name_(self):
        for r in self:
            name = r.get_names()
            r.name = name
    @api.depends('gio_bat_dau')
    def ngay_bat_dau_(self):#trong su kien
        for r in self:
            if r.gio_bat_dau:
                r.ngay_bat_dau = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau).date()
#     @api.depends('gio_bat_dau')
#     def ngay_bat_dau2_(self):#trong su kien
#         for r in self:
#             if r.gio_bat_dau:
#                 utc_datetime_inputs = fields.Datetime.from_string(r.gio_bat_dau)
#                 r.date = utc_datetime_inputs.date()            
    
    @api.depends('gio_ket_thuc','gio_bat_dau')
    def _get_duration(self):
        for r in self:
            if r.gio_bat_dau == False or r.gio_ket_thuc==False:
                r.duration = False
            else:
                start_date = fields.Datetime.from_string(r.gio_bat_dau)
                end_date = fields.Datetime.from_string(r.gio_ket_thuc)
                duration = (end_date - start_date)
                secs = duration.total_seconds()
                hour = secs / 3600
                r.duration = hour    
                
    @api.multi
    def write(self,vals):
        rs = super(CviSuCo, self).write(vals)
        for r in self:
            if vals.get(u'loai_record') and vals.get(u'loai_record') != u'Công Việc' and  r.loai_record ==u'Công Việc':
                raise UserError(u'không được thay đổi record từ công việc sang cái khác')
        return rs