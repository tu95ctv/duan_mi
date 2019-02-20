# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions,tools,_
import sys
VERSION_INFO   = sys.version_info[0]
class LTKSetting(models.TransientModel):
    _name = 'ltk.config.settings'
    _inherit = 'res.config.settings'
    is_cam_sua_do_time  =fields.Boolean(string=u'Có cấm sửa do quá thời gian?')
    is_cam_sua_truoc_ngay =fields.Boolean(string=u'Có cấm sửa trước ngày?')
    cam_sua_truoc_ngay = fields.Date(string=u'Cấm sửa trước ngày')
    allow_edit_time = fields.Integer(string = u'Thời gian cho phép để sửa record (giây)',default=20)
    
    is_show_loai_record =fields.Boolean(string=u'Show loại record trong BCN?')


    
#     group_show_cot_lanh_dao = fields.Selection([
#         (0, u'Không show cột lãnh đạo'),
#         (1, u'show cột lãnh đạo')
#         ], u"Show cột lãnh đạo", implied_group='dai_tgg.show_cot_lanh_dao_group')
    group_co_tvcv_giai_doan_con = fields.Selection([
        (0, u'Không show TVCV con'),
        (1, u'Show TVCV con')
        ], u"TVCV Con", implied_group='dai_tgg.show_tvcv_con')
    group_show_thong_tin_create_write = fields.Selection([
        (0, u'Không show thông tin create và  và không show thông tin write'),
        (1, u'Show thông tin create và  show thông tin write')
        ], u"Show thông tin create, write", implied_group='dai_tgg.show_thong_tin_create_write')
   
    
        
    @api.multi
    def set_values(self):
        super(LTKSetting, self).set_values()
        for fname in [ 'is_cam_sua_truoc_ngay','cam_sua_truoc_ngay','allow_edit_time','is_cam_sua_do_time','is_show_loai_record']:
            if VERSION_INFO==2:
                self.env['ir.values'].sudo().set_default(
            'ltk.config.settings',fname,getattr(self, fname))
            else:
                self.env['ir.config_parameter'].sudo().set_param('dai_tgg.'+fname, getattr(self, fname))
    @api.model
    def get_values(self):
        res = super(LTKSetting, self).get_values()
        for fname in ['cam_sua_truoc_ngay','is_cam_sua_truoc_ngay','is_cam_sua_do_time','is_show_loai_record']:   
            res.update(
               {fname:self.env['ir.config_parameter'].sudo().get_param('dai_tgg.' + fname)}
            )
        for fname in ['allow_edit_time']:
            res.update(
               {fname:int(self.env['ir.config_parameter'].sudo().get_param('dai_tgg.' + fname))}
            )
            
        return res
    
    
    