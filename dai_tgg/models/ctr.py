# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import  convert_memebers_to_str,convert_utc_to_gmt_7,name_compute,convert_odoo_datetime_to_vn_datetime,convert_odoo_datetime_to_vn_str,convert_vn_datetime_to_utc_datetime,Convert_date_orm_to_str
import datetime
from odoo.exceptions import UserError
from unidecode import unidecode
class CTR(models.Model):
    _name = 'ctr'
#     test_id = fields.Many2one('res.partner')
    name = fields.Char(compute = '_name_truc_ca_compute', store=True)
    name_khong_dau = fields.Char(compute = '_name_truc_ca_compute', store=True)
    ca = fields.Selection([(u'Sáng',u'Sáng'), (u'Chiều',u'Chiều'), (u'Đêm',u'Đêm')],string=u'Buổi ca',default = lambda self: self.buoi_ca_now_default_())
    date = fields.Date(string=u'Ngày',default= convert_utc_to_gmt_7(datetime.datetime.now()).date() )#readonly = True
    gio_bat_dau_ca = fields.Datetime(u'Giờ bắt đầu ca ',default=lambda self: self.gio_bat_dau_defaut_or_ket_thuc_())
    gio_ket_thuc_ca = fields.Datetime(u'Giờ Kết Thúc ca',default=lambda self: self.gio_bat_dau_defaut_or_ket_thuc_(is_tinh_gio_bat_dau_or_ket_thuc = 'gio_ket_thuc'))#
    department_id = fields.Many2one('hr.department',string=u'Đơn vị',default=lambda self:self.env.user.department_id, readonly=True, required=True,ondelete='restrict')
    member_ids = fields.Many2many('res.users', string=u'Những thành viên trực',default =  lambda self : [self.env.user.id],required=True)
    cvi_ids = fields.One2many('cvi','ctr_id',string=u'Công Việc/Sự Cố/Sự Vụ')
    cvi_show =  fields.Char(compute='cvi_show_',string=u'Công Việc/Sự Cố/ Sự Vụ')
    ton_dong_ca_truoc_ids = fields.Many2many('cvi',string=u'Tồn đọng ca trước')
    ton_dong_show_number =  fields.Integer(default=20,string=u'Số dòng tồn động muốn hiển thị')
    
    @api.onchange('member_ids')
    def member_ids_oc(self):
        truc_ca_tvcv_id =  self.env['tvcv'].search([('name','=',u'Trực ca')])
        cvi_ids_tvcv =  self.cvi_ids.mapped('tvcv_id')
        if  (not cvi_ids_tvcv or truc_ca_tvcv_id == cvi_ids_tvcv) :#and not self.cvi_ids:
            new_trucca_cvi = list(map(lambda m:(0,0,{'user_id':m,'loai_record':u'Công Việc','tvcv_id':truc_ca_tvcv_id.id,'state':'confirmed'}),self.member_ids))
            return {'value':
                                    {'cvi_ids': new_trucca_cvi}
                    }
    @api.onchange('ton_dong_show_number')
    def ton_dong_ca_truoc_ids_(self):
        for r in self:
            domain =['|',('is_giao_ca','=',True),('gio_ket_thuc','=',False)]
            ton_dong_ca_truoc_ids = self.env['cvi'].search(domain,limit=self.ton_dong_show_number,order='id desc')
            r.ton_dong_ca_truoc_ids = ton_dong_ca_truoc_ids
#     @api.depends('cvi_ids')
#     def cvi_show_(self):
#         for r in self:
#             try:
#                 r.cvi_show = u' | '.join(r.cvi_ids.mapped('name'))
#             except TypeError:
#                 pass
            
    @api.depends('cvi_ids')
    def cvi_show_(self):
        for r in self:
            cvi_ids = r.cvi_ids
            if cvi_ids:
                r.cvi_show = u' | '.join(list(map(lambda r: r.get_names(),cvi_ids)))
          
    def get_names(self):
            name = name_compute(self,
            adict=[('id',{'pr':u'Ca Trực id'}),
                   ('date',{'pr':u'Ngày','func':Convert_date_orm_to_str}),
                   ('ca',{'pr':u'Buổi'}),
                    ('member_ids',{'pr':u'Người Trực','func':convert_memebers_to_str})
                   ]
                                 )
            return name
    @api.multi
    def name_get(self):
        return [(r.id, r.get_names()) for r in self]
#     @api.model
#     def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
#         res = super(CTR, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type =='form':
#             id_you_want = self._context.get('active_id')
#             fields = res.get('fields')
#             fields['date']['string'] =u'anh con no'# ['|',('ctr_ids','=','active_id'),'&',('ctr_ids','!=',False),('gio_ket_thuc','=',False)]
#             fields['loai_su_co']['domain'] ='''[('l','!=',False)]'''
#         return res
    @api.depends('date','ca','member_ids')
    def _name_truc_ca_compute(self):
        for r in self:
            ret =  r.get_names()
            r.name = ret
            if ret:
                r.name_khong_dau = unidecode(ret)
    
#     @api.depends('gio_bat_dau_ca')
#     def date_(self):
#         for r in self:
#             if r.gio_bat_dau:
#                 r.date = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau).date()
    def buoi_ca_now_default_(self,gio_bat_dau_vn_return = False):
        now_vn_datetime = convert_utc_to_gmt_7(datetime.datetime.now())
        now_hour = now_vn_datetime.hour
        alist = [(u'Sáng',7),(u'Chiều',14),(u'Đêm',22)]
        new_list= list(map(lambda i:abs(now_hour-i[1]),alist))
        index =  new_list.index(min (new_list))
        buoi_ca = alist[index][0]
        if gio_bat_dau_vn_return:
            return buoi_ca,now_vn_datetime
        else:
            return buoi_ca
    def gio_bat_dau_defaut_or_ket_thuc_(self,is_tinh_gio_bat_dau_or_ket_thuc = 'gio_bat_dau'):#dd/mm/Y 14:00:00
        adict = {u'Sáng':'sang',u'Chiều':'chieu',u'Đêm':'dem'}
        buoi_ca,now_vn_datetime =  self.buoi_ca_now_default_(gio_bat_dau_vn_return = True)
        ca_x_bat_dau_key = 'ca_' + adict[buoi_ca] + '_bat_dau'
        get_ca_x_bat_dau_from_congty = getattr(self.env.user.department_id,ca_x_bat_dau_key)
        if get_ca_x_bat_dau_from_congty==False:
            return datetime.datetime.now()
        x =  now_vn_datetime.strftime('%d-%m-%Y')
        x = x + ' ' +get_ca_x_bat_dau_from_congty
        native_ca_gio_in_vn  = datetime.datetime.strptime(x,'%d-%m-%Y %H:%M:%S')
        gio_bat_dau_in_utc = convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn)
        if is_tinh_gio_bat_dau_or_ket_thuc == 'gio_bat_dau':
            return gio_bat_dau_in_utc   
        else:
            ca_x_duration_key = 'ca_' + adict[buoi_ca] + '_duration'
            duration_hours = getattr(self.env.user.department_id,ca_x_duration_key)
            if duration_hours:
                gio_ket_thuc_utc = gio_bat_dau_in_utc + datetime.timedelta(hours=duration_hours,seconds=-1)
                return gio_ket_thuc_utc
            else:
                return False
    
    @api.model
    def create(self, vals):
        new_ctx = dict(self._context, **{'write_create_parent_dict':vals})
        print ('***vals in create of ca truc',vals)
        cv = super(CTR, self.with_context(new_ctx)).create(vals)
        return cv

    @api.multi
    def write(self, vals):
        print ('vals in write of catruc', vals)
#         print ('vals in write',vals)
#         if 'slncl' in vals:
#             raise UserError(u'kkakaka')
#         if 'cd_parent_id' in vals:
#             raise UserError(u'cd_parent_id %s'%vals)
        new_ctx = dict(self._context, **{'write_create_parent_dict':vals})
        res = super(CTR, self.with_context(new_ctx)).write(vals)
        return res    
    
#     @api.model
#     def default_get(self, fields):
#         res = super(CTR, self).default_get(fields)
# #         adict = {'cvi_ids':{'model':'cvi','domain':[('gio_ket_thuc','=',False),('ctr_ids','!=',False),('department_ids','=',self.env.user.department_id.id)]},
#         adict = {'cvi_ids':{'model':'cvi','domain':[('gio_ket_thuc','=',False),('ctr_ids','!=',False),'|',('department_id','=',self.env.user.department_id.id),('department_ids','=',self.env.user.department_id.id)]},
# #                  'su_co_ids':{'model':'suco','add_domain':[('ctr_ids','!=',False)]},
# #                  'su_vu_ids':{'model':'suvu','add_domain':[('ctr_ids','!=',False)]}
#               
#                  }
#         #def afunc(atuple):
#         print ('defaut_get************')
#         for field,attr_field_dict in adict.items():
#             model = attr_field_dict['model']
#             domain=  attr_field_dict['domain']
#             empty_ket_thuc_comments = self.env[ model].search(domain)
#             if empty_ket_thuc_comments:
#                 res[field] = empty_ket_thuc_comments.mapped('id')
# #         res['member_ids']  = [self.env.user.id]
#         return res           
