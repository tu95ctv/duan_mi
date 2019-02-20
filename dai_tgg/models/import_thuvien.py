# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import default_import_xl_setting

# from odoo.addons.dai_tgg.models.tao_instance import import_strect

# from odoo.addons.dai_tgg.models.model_dict import gen_model_dict

# ALL_MODELS_DICT = ALL_MODELS_DICT



class ImportThuVien(models.Model):
    _name = 'importthuvien' 
    type_choose = fields.Selection([
#         (u'stock.inventory.line',u'stock.inventory.line'),
#         (u'stock.inventory.line.dp_tti',u'stock.inventory.line.dp_tti'),
        (u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',u'stock.inventory.line.tong.hop'),
#         (u'stock.inventory.line.tkt.vtdc',u'stock.inventory.line.tkt.vtdc'),
        (u'Product',u'Product'),
        (u'Thư viện công việc',u'Thư viện công việc'),
        (u'User',u'User')
        ,(u'Department',u'Department')
        ,(u'Partner',u'Partner')
        ,(u'location partner',u'location partner')
        ,(u'categ',u'Product Category')
        ,(u'cvi',u'Công việc')
         ,(u'thuebaoline',u'Thuê bao'),
         (u'Loại sự cố, sự vụ', u'Loại sự cố, sự vụ')
                                    ],required = True,default=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp')
    sheet_name_select = fields.Selection([
                                    (u'Vô tuyến',u'Vô tuyến'),
                                  (u'TRUYỀN DẪN',u'TRUYỀN DẪN'),
                                   (u'Chuyển Mạch (IMS, Di Động)',u'Chuyển Mạch (IMS, Di Động)'),
                                   (u'Truyền dẫn',u'Truyền dẫn'),(u'IP (VN2, VNP)',u'IP (VN2, VNP)'),
                                   (u'GTGT',u'GTGT'),(u'XFP, SFP các loại',u'XFP, SFP các loại')  ],rejquired=True)
    sheet_name =  fields.Char()
    key_tram =  fields.Selection([('key_ltk','key_ltk'),
                                  ('key_tti','key_tti'),
                                  ('key_137','key_137'),
                                  ('key_tti_dc','key_tti_dc'),
                                  ('key_ltk_dc','key_ltk_dc'),
                                  ('key_ltk_dc2','key_ltk_dc2'),
                                  ],default='key_ltk')
    mode_no_create_in_main_instance = fields.Boolean()
    file = fields.Binary()
    filename = fields.Char()
    name_inventory_suffix = fields.Char()
    department_id = fields.Many2one('hr.department')
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    thong_bao_khac = fields.Char()
    trigger_model = fields.Selection([(u'kiemke',u'kiemke'),
                                    (u'vattu',u'vattu'),
                                    (u'kknoc',u'kknoc'),
                                    (u'cvi',u'cvi'),
                                    (u'stock.production.lot',u'stock.production.lot')
                                    ])
    dong_test = fields.Integer(default=0)#0 la initify vô hạn
    log = fields.Text()
    skip_field_cause_first_import = fields.Boolean(default=True)
    begin_row = fields.Integer(default=0)
#     location_id = fields.Many2one('stock.location')
    running_or_prepare = fields.Selection([('running',u'Đang chạy'),('prepare',u'Dự phòng')])
    import_location_id = fields.Many2one('stock.location')
    imported_number_of_row = fields.Integer()
    inventory_id = fields.Many2one('stock.inventory')
    test_result_1 = fields.Text()
    test_result_2 = fields.Text()
    test_result_3 = fields.Text()
    line_not_has_quant =  fields.Text()
    only_xuat_thuoc_tinh =  fields.Boolean()
    dac_tinh = fields.Char()
    categ_id = fields.Many2one('product.category')
    
    
    
#     default_import_xl_setting = {'default_cho_phep_exist_val_before_loop_fields_func':True,
#              'default_write_when_val_exist':False,
#              'default_allow_check_excel_obj_is_exist_func':False,
#              'default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':False,
#              'default_cho_phep_co_pn_cap_nhat_empty_pn':False,
#              }

    
    cho_phep_exist_val_before_loop_fields_func = fields.Boolean(default = default_import_xl_setting['default_cho_phep_exist_val_before_loop_fields_func'])
    write_when_val_exist  = fields.Boolean(default = default_import_xl_setting['default_write_when_val_exist'])
    allow_check_excel_obj_is_exist_func  = fields.Boolean(string=u'Cho phép đối chiếu product excel obj với product exist object',default = default_import_xl_setting['default_allow_check_excel_obj_is_exist_func'])
    cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat  = fields.Boolean(default = default_import_xl_setting['default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat'])
    cho_phep_co_pn_cap_nhat_empty_pn  = fields.Boolean(default = default_import_xl_setting['default_cho_phep_co_pn_cap_nhat_empty_pn'])
    
    
    
    is_admin = fields.Boolean(compute='is_admin_')
    mode = fields.Selection([(u'1',u'mode 1 (tim location goc bằng key)'),(u'2',u'mode 2 ( tìm location góc bằng cột trạm)')])
    @api.onchange('sheet_name_select')
    def sheet_name_select_oc_(self):
        if self.sheet_name_select:
            self.sheet_name = self.sheet_name_select
    @api.depends('type_choose')
    def is_admin_(self):
        for r in self:
            r.is_admin = self.user_has_groups('base.group_erp_manager')
    
    def importthuvien(self):
        importthuvien(self)
        return True
   
    def import_all(self):
#         importthuvien(self,key=u'User')
        importthuvien(self,key=u'Department')
        importthuvien(self,key=u'Partner')
        importthuvien(self,key=u'location partner')
        importthuvien(self,key= u'Loại sự cố, sự vụ')
        importthuvien(self,key= u'thuebaoline')
        importthuvien(self,key= u'categ')
        return True
    
    
    
    
    @api.onchange('type_choose')
    def import_location_id_(self):
#         adict = {'stock.inventory.line':'prepare','stock.inventory.line.tkt.vtdc':'running'}
        if self.type_choose == u'stock.inventory.line':
            self.import_location_id = self.env['stock.location'].search([('name','=',u'LTK Dự Phòng')]).id
        elif self.type_choose == u'stock.inventory.line.tkt.vtdc':
            self.import_location_id = self.env['stock.location'].search([('name','=',u'LTK Đang Chạy')]).id
    
    
    def check_stt_inventory_line_old(self):
        rs = self.env['stock.inventory.line'].search([('inventory_id','=',self.inventory_id.id)], order='stt asc')
        rs2 = self.env['stock.inventory.line'].search([('inventory_id','=',self.inventory_id.id)], order='stt desc',limit=1)
        last_stt = rs2.stt
        kq = set(rs.mapped('stt'))
        self.test_result_1  = kq
        set_2 = set(range(1,last_stt))
        self.test_result_2= last_stt
        rs3 = set_2 - kq
        self.test_result_3 = sorted(rs3) 
    def check_line_khong_co_quant_va_khong_co_qty(self):
        rs1 = self.inventory_id.line_ids
        khong_co_so_luong =  sorted( rs1.filtered(lambda r: not  r.product_qty ).mapped('stt'))
        co_so_luong_but_khong_co_quant = sorted( rs1.filtered(lambda r: r.product_qty and not r.quant_ids).mapped('stt'))
        self.test_result_3 ='co_so_luong_but_khong_co_quant' + '\n%s'%co_so_luong_but_khong_co_quant
        self.test_result_2= 'khong_co_so_luong \n%s'%khong_co_so_luong
    def check_stt_inventory_line(self):
        rs1 = self.inventory_id.line_ids
        rs2 = rs1.mapped('quant_ids').filtered(lambda r: r.location_id.usage=='internal')
        rs3 = sorted(rs2.mapped('stt'))
#         rs2 =sorted( rs1.filtered(lambda r: r.product_qty and not r.quant_ids).mapped('stt'))
        self.test_result_1 =len(rs1)
        self.test_result_2 =len(rs2)
        self.test_result_3= rs3
        
    def test_code(self):
        fields=self.env['stock.move.line']._fields
#         print ('fields',fields)
        self.test_result_1 = dir(fields['product_id'])
        self.test_result_2 = fields['product_id'].required
        print ("fields['product_id'].required",fields['product_id'].required)
    def test_code1(self):
#         sql_multi_2 = '''select date_trunc('day',create_date) from stock_quant'''
         
        sql_multi_2 = "select create_date at time zone 'UTC' at time zone 'ICT'  from stock_quant where cast(create_date at time zone 'UTC' at time zone 'ICT' as date) = date '2018-08-31 '"
        self.env.cr.execute(sql_multi_2)
        result_2 = self.env.cr.dictfetchall()
        self.test_result_1 = result_2
        print ('self._context',self._context)

#         self.env['stock.inventory'].browse([13]).line_ids.unlink()
    def trigger(self):
        if self.trigger_model:
            count = 0
            self.env[self.trigger_model].search([]).write({'trig_field':'ok'})

        else:
            raise UserWarning(u'Bạn phải chọn trigger model')
    
    def import_strect(self):
        pass
        return True


class ImportCVI(models.Model):
    _name='dai_tgg.importcvi'
    _inherit = 'importthuvien'
    user_id = fields.Many2one('res.users',default= lambda self:self.env.uid)
    
    @api.model
    def default_get(self, fields):
        rs = super(ImportCVI, self).default_get(fields)
        rs['type_choose'] = u'cvi'
        return rs

    