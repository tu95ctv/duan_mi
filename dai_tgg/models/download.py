# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.dai_tgg.models.dl_models.dl_tvcv import  download_tvcv
from odoo.addons.dai_tgg.models.dl_models.dl_user import  download_user

from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_bcn
from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_cvi

from odoo.addons.dai_tgg.models.dl_models.dl_p3 import  dl_p3,gen_read_group_domain_user_in_department,gen_date_and_department_domain
from odoo.addons.downloadwizard.download_tool import  do_if_model_name_wrapper


class ThongkeDiemCVILine(models.TransientModel):
    _name = 'daitgg.thongkediemcviline'
    user_id = fields.Many2one('res.users')
    user_id_count = fields.Integer(string=u'Số lượng công việc')
    diemtc = fields.Float(digits=(6,2),string=u'Điểm Nhân Viên',store=True)
    diemld = fields.Float(digits=(6,2),string=u'Điểm Lãnh Đạo Chấm',store=True)
    download_id = fields.Many2one('downloadwizard.download')

# def do_if_model_name_wrapper(model_name):
#     def do_if_model_name(func):
#         def f_wrapper(self):
#             if self.model_name =='download_bcn':
#                 func(self)
#             else:
#                 pass
#         return f_wrapper
#     return do_if_model_name

class DownloadCVI(models.TransientModel):
    _inherit = "downloadwizard.download"
#     _name =  "dai_tgg.downloadcvi"
    date = fields.Date(default=fields.Date.context_today,string=u'Ngày bắt đầu')
    end_date = fields.Date(default=fields.Date.context_today,string=u'Ngày kết thúc')
    chon_thang = fields.Selection([(u'Tháng Trước',u'Tháng Trước'),(u'Tháng Này',u'Tháng Này')],string = u'Chọn tháng',default=u'Tháng Này')
    department_id = fields.Many2one('hr.department',u'Đơn vị (Trạm)')
    chi_tiet_hay_danh_sach = fields.Selection([('chi_tiet',u'Chi tiết'),('danh_sach',u'Danh Sách')],u'Chọn xuất chi tiết hay danh sách')
    
    diem_line_ids = fields.One2many('daitgg.thongkediemcviline','download_id',string=u'Tổng điểm nhân viên trong khoản thời gian chọn')
    is_write_diem = fields.Boolean(string=u'Bạn có muốn ghi đè điểm thư viện không')
    diff_diem_tvcv_count =  fields.Integer(u'Số lượng cvi có điểm khác với điểm thư viện')
    bcn_cvi_ids =  fields.Many2many('cvi','wizard_cvi_relate','wizard_id','cvi_id',store=False,compute='bcn_cvi_ids_',string=u'Những công việc/sự cố sẽ báo cáo')
    bcn_thue_bao_line_ids = fields.Many2many('dai_tgg.thuebaoline','wizard_cvi_thuebaoline_relate','wizard_id','thuebaoline_id',store=False,compute='bcn_thue_bao_line_ids_',string=u'Những dòng thuê bao sẽ báo cáo')
    
    
    
    @api.depends('date')
    @do_if_model_name_wrapper('download_bcn')
    def bcn_thue_bao_line_ids_(self):
        bcn_thue_bao_line_ids = self.env['dai_tgg.thuebaoline'].search([('date','=',self.date)],order='id asc')
        self.bcn_thue_bao_line_ids = bcn_thue_bao_line_ids
    
    @api.depends('date')
    @do_if_model_name_wrapper('download_bcn')
    def bcn_cvi_ids_(self):
        cvi = self.env['cvi'].search([('is_bc','=',True),('ngay_bat_dau','=',self.date)],order='id asc')
        self.bcn_cvi_ids = cvi
    
    def  oc_to_diem(self):
        read_group_rsul = gen_read_group_domain_user_in_department(self)
        rt = map(lambda m:(0,0,{'user_id':m['user_id'][0],'user_id_count':m['user_id_count'],'diemtc':m['diemtc'],'diemld':m['diemld']}),read_group_rsul)
        rt = list(rt)
        return rt
    @api.onchange('date','end_date','chon_thang','department_id')
    def oc_to_diem_line_ids_(self):
#         read_group_rsul = gen_read_group_domain_user_in_department(self)
#         rt = map(lambda m:(0,0,{'user_id':m['user_id'][0],'user_id_count':m['user_id_count'],'diemtc':m['diemtc'],'diemld':m['diemld']}),read_group_rsul)
#         rt = list(rt)
        
        rt = self.oc_to_diem()
        return {'value':
                {'diem_line_ids':rt
                 }
                }
        
        
    
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadCVI, self).gen_pick_func()
        pick_func = {'tvcv':download_tvcv,'res.users':download_user,'download_bcn':dl_bcn,'cvi': dl_cvi,'download_p3':dl_p3}
        rs.update(pick_func)
        return rs
    @api.multi
    def gen_model_verbal_dict(self): 
        rs = super(DownloadCVI, self).gen_model_verbal_dict()
        rs.update({'stock.quant':u'Kho','product.product':u'Vật tư','download_bcn':u'Báo cáo ngày','download_p3':u'Download P3'})
        return rs
    @api.multi
    def update_tvcv_diem_to_cvi(self):
        domain = gen_date_and_department_domain(self)
        congviecs = self.env['cvi'].search(domain)
        diff_diem_tvcv_count =0
        print ('***congviecs',congviecs)
        for cvi in congviecs:
            print ('****',cvi.tvcv_id.diem,cvi.diem_tvi)
            if cvi.tvcv_id.diem != cvi.diem_tvi:
                diff_diem_tvcv_count +=1
                if self.is_write_diem:
                    cvi.diem_tvi = cvi.tvcv_id.diem
        self.diff_diem_tvcv_count=diff_diem_tvcv_count
        rt = self.oc_to_diem()
        self.diem_line_ids = False
        self.diem_line_ids = rt
#         self.write({'diem_line_ids':rt
#                  })
#         
        
        model =self._context.get('transfer_active_model') or self._context['active_model']
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'downloadwizard.download',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'context':{'active_model':model},
            'views': [(False, 'form')],
            'target': 'new',
        }

        
    
    
    