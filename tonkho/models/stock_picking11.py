# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from datetime import timedelta
from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import gen_model_dict,default_import_xl_setting
from odoo.addons.tonkho.models.dl_models.xl_tranfer_bb import write_xl_bb
from odoo.addons.tonkho.models.check_file import check_imported_file_sml

import base64
import contextlib
import io

from xlutils.copy import copy### phai install moi 
# from xlrd import *
import xlrd
import inspect
import os

from lxml import etree

BG_lst = [
          (u'BBBG',u'Giao'),
          (u'NHAN',u'Nhận'),
          (u'TRVT',u'Trình vật tư'),
           (u'BBNT',u'Nghiệm thu'),
           (u'BBSD',u'Đưa vào sử dụng'),
        #   (u'BBNK',u'Nhập kho vật tư lỗi'),
           (u'HUY',u'Biên bản hủy'),
           (u'TRA_DO_HUY',u'Trả do hủy biên bản'),
           (u'TRA_DO_MUON',u'Trả do mượn'),
           (u'CHUYEN_TIEP',u'Chuyển tiếp'),
           (u'TDTT',u'Thay đổi tình trạng vật tư'),
           (u'DCNB',u'Dịch chuyển nội bộ'),
           ]
BG_dict = dict(BG_lst)
def _select_nextval(cr, seq_name):
    cr.execute("SELECT nextval('%s')" % seq_name)
    return cr.fetchone()
class ToTrinh(models.Model):
    _name = 'tonkho.title_cac_ben'
    name = fields.Char(u'Title',required=True)
class StockPicking(models.Model):
    _inherit = "stock.picking"
#     cancel_mode = fields.Boolean(compute='action_cancel_show_')
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per company!'),
        ('name_ma_bb', 'unique(stt_trong_bien_ban_in,department_id,ban_giao_or_nghiem_thu)', u'Mã BBBG và số TT trong bản phải là duy nhất trên mỗi phòng ban!'),
    ]
    
    
    # field ghi đè
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done_ben_giao', u'Xác nhận bên giao'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")
    
    # Công cụ
    categ_id = fields.Many2one('product.category',string=u'Thay đổi nhóm cho các dòng điều chuyển')
    
    
   
    # Field chính trong biên bản

    name = fields.Char(
        compute='name_',store=True,
        string='Reference',
        copy=False,  index=True,
        )
    @api.depends('department_id','ban_giao_or_nghiem_thu','stt_trong_bien_ban_in')
    def name_(self):
        name = self.department_id.short_name + '/' + '%s'%BG_dict[self.ban_giao_or_nghiem_thu] + '/%s'%self.stt_trong_bien_ban_in
        self.name = name
        
    # xem lại
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default= lambda self: self.env['stock.picking.type'].search(['|',('name','=',u'Dịch chuyển nội bộ'),('name','=','Internal Transfers')])[0].id
        )
    
    texttemplate_id = fields.Many2one('tonkho.texttemplate',string=u"Mẫu lý do",domain=[('field_context','=','tonkho.stock.picking.field.ly_do')],copy=False)
    ly_do = fields.Text(u'Lý do',copy=False)#Tình trạng vật tư: Vật tư đang sử dụng lỗi, đem SVTECH bảo hành,
    
    totrinh_id = fields.Many2one('dai_tgg.totrinh', string=u'Tờ trình',copy=False)
    noi_ban_giao = fields.Many2one('res.partner',default= lambda self: self.env.user.department_id.partner_id, string=u'Nơi bàn giao',copy=False)
    department_id = fields.Many2one('hr.department',
                                    default=lambda self:self.env.user.department_id,
                                    string=u'Đơn vị',
                                    required=True,copy=False)
    
    
    stt_trong_bien_ban_in = fields.Integer(string=u'STT trong biên bản',compute='stt_trong_bien_ban_in_',store=True,copy=False)
    @api.depends('department_id','ban_giao_or_nghiem_thu')
    def stt_trong_bien_ban_in_(self):
        for r in self:
            domain = [('department_id','=',self.department_id.id),
                                                        ('ban_giao_or_nghiem_thu','=',r.ban_giao_or_nghiem_thu),
                                                        ('stt_trong_bien_ban_in','!=', 0),
                                                        ]
            if isinstance(r.id, int):
                domain.append(('id','!=',r.id))
            picking = self.env['stock.picking'].search(domain, limit=1, order='stt_trong_bien_ban_in desc')
            if picking:
    #             self.env.cr.execute('select stt_trong_bien_ban_in from stock_picking where id =%s'%picking.id)
    #             ad =  self.env.cr.dictfetchall()
    #             print ('ad',ad)
    #             stt_trong_bien_ban_in = ad[0]['stt_trong_bien_ban_in'] + 1
                stt_trong_bien_ban_in = picking.stt_trong_bien_ban_in + 1
    #             print ('stt_trong_bien_ban_in',stt_trong_bien_ban_in)
                r.stt_trong_bien_ban_in = stt_trong_bien_ban_in
            else:
                r.stt_trong_bien_ban_in = 1
                
    ban_giao_or_nghiem_thu = fields.Selection(BG_lst,default=u'BBBG', string=u'B/giao hay N/thu',copy=False)
    
    
#     location_id_partner_id =  fields.Many2one('res.partner',related='location_id.partner_id_of_stock_for_report',store=False,readonly=True)
    is_required_doi_tac_giao =  fields.Boolean(compute='is_required_doi_tac_giao_')
    @api.depends('location_id')
    def is_required_doi_tac_giao_(self):
        for r in self:
            location_id_name =  r.location_id.name
            if location_id_name in [u'Đối tác giao',u'Đối tác nhận']:
                r.is_required_doi_tac_giao = True
    
#     location_dest_id_partner_id =  fields.Many2one('res.partner',related='location_dest_id.partner_id_of_stock_for_report',store=False,readonly=True)
    is_required_doi_tac_nhan =  fields.Boolean(compute='is_required_doi_tac_nhan_')
    @api.depends('location_dest_id')
    def is_required_doi_tac_nhan_(self):
        for r in self:
            location_id_name =  r.location_dest_id.name
            if location_id_name in [u'Đối tác giao',u'Đối tác nhận']:
                r.is_required_doi_tac_nhan = True
                
    doi_tac_giao_id = fields.Many2one('res.partner',u'Đơn vị  giao',copy=False)
    doi_tac_nhan_id = fields.Many2one('res.partner',u'Đơn vị nhận', copy=False)
    # Field thêm để lọc         
    choosed_stock_quants_ids = fields.Many2many('stock.quant',compute='choosed_stock_quants_ids_',store=False)
    
    
    sheet_name = fields.Char()
    sheet_name_select = fields.Selection([
                                   (u'All',u'All'),
                                   (u'Vô tuyến',u'Vô tuyến'),
                                   (u'Chuyển mạch',u'Chuyển mạch'),
                                   (u'Truyền dẫn',u'Truyền dẫn'),
                                   (u'IP',u'IP'),
                                   (u'GTGT',u'GTGT'),
                                   (u'Khác',u'Khác'),
                                   (u'XFP, SFP các loại',u'XFP, SFP các loại')  ],rejquired=True)
    
    
    sheet_name =  fields.Char()
    @api.onchange('sheet_name_select')
    def sheet_name_select_oc_(self):
        if self.sheet_name_select:
            self.sheet_name = self.sheet_name_select
    
    @api.depends('move_line_ids.stock_quant_id')
    def choosed_stock_quants_ids_(self):
        for r in self:
            r.choosed_stock_quants_ids =  r.move_line_ids.mapped('stock_quant_id')
            
            
    is_admin = fields.Boolean(compute='is_admin_')
    @api.depends('name')
    def is_admin_(self):
        for r in self:
            if self.user_has_groups('base.group_erp_manager'):
                r.is_admin = True
    
    # valid mode
    show_validate_ben_giao = fields.Boolean(compute='show_validate_ben_giao_')
    @api.depends('location_id','location_dest_id')
    def show_validate_ben_giao_(self):
        for r in self:
            if r.is_validate_mode:
                if r.is_admin:
                    r.show_validate_ben_giao = True
                    return True
                ban_la_ben_giao = self.env.user.department_id == r.location_id.department_id 
                if ban_la_ben_giao and not r.is_same_department and r.state not in ('done','done_ben_giao') :
                    show_validate_ben_giao = True
                else:
                    show_validate_ben_giao = False
            else:
                show_validate_ben_giao = False
            r.show_validate_ben_giao = show_validate_ben_giao
            
    is_validate_mode = fields.Boolean(compute='is_validate_mode_')
    @api.multi
    def is_validate_mode_(self):
        for r in self:
            r.is_validate_mode = self.env['ir.config_parameter'].sudo().get_param('tonkho.is_validate_mode')
        
    is_same_department = fields.Boolean(compute='is_same_department_')
    @api.depends('location_id','location_dest_id')
    def is_same_department_(self):
        for r in self:
            is_same_department = r.location_id.department_id == r.location_dest_id.department_id
            if not is_same_department:
                is_same_department = not r.location_id.department_id and r.location_id.cho_phep_khac_tram_chon
                is_same_department =  is_same_department or  (not r.location_dest_id.department_id and r.location_dest_id.cho_phep_khac_tram_chon)
            r.is_same_department = is_same_department
            
    # thông tin thêm
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên giao',copy=False)
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên nhận',copy=False)
    file_ids = fields.Many2many('dai_tgg.file','stock_picking_file_relate','stock_picking_id','file_id',string=u'Files đính kèm')
    title_ben_thu_3 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 3',copy=False)
    ben_thu_3_ids = fields.Many2many('res.partner','ben_thu_3_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 3',copy=False)
    title_ben_thu_4 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 4',copy=False)
    ben_thu_4_ids = fields.Many2many('res.partner','ben_thu_4_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 4',copy=False)
    lanh_dao_id = fields.Many2one('res.partner',string=u'Lãnh Đạo')
    so_ban_in = fields.Integer(u'Số bản in',default=4,copy=False)
    ben_giao_giu = fields.Integer(u'Bên giao giữ', default=3,copy=False)
    ben_nhan_giu = fields.Integer(u'Bên nhận giữ',default=1,copy=False)
    # import file
    file = fields.Binary(string='File Import')
    filename = fields.Char()
    
#     default_import_xl_setting = {'default_cho_phep_exist_val_before_loop_fields_func':True,
#              'default_write_when_val_exist':False,
#              'default_allow_check_excel_obj_is_exist_func':False,
#              'default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':False,
#              'default_cho_phep_co_pn_cap_nhat_empty_pn':False,
#              }
#    
    cho_phep_exist_val_before_loop_fields_func = fields.Boolean(default = default_import_xl_setting['default_cho_phep_exist_val_before_loop_fields_func'])
    write_when_val_exist  = fields.Boolean(default = default_import_xl_setting['default_write_when_val_exist'])
    allow_check_excel_obj_is_exist_func  = fields.Boolean(string=u'Cho phép đối chiếu product excel obj với product exist object',default = default_import_xl_setting['default_allow_check_excel_obj_is_exist_func'])
    cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat  = fields.Boolean(default = default_import_xl_setting['default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat'])
    cho_phep_co_pn_cap_nhat_empty_pn  = fields.Boolean(default = default_import_xl_setting['default_cho_phep_co_pn_cap_nhat_empty_pn'])
    
    
    skip_stt = fields.Boolean(u'Skip (bỏ qua) trường STT khi import')
    allow_cate_for_ghi_chu =  fields.Boolean(string=u"Lấy Tiêu đề làm ghi chú")
    range_1 = fields.Integer(string=u'stt dòng tiêu đề đầu')
    range_2 = fields.Integer(string=u'stt dòng tiêu đề cuối')
    log = fields.Text()
    # check file
    is_ghom_tot = fields.Boolean(string=u'Nếu tình trạng vật tư tốt hết thì ko cần ghi trong cột',default = True)
    file_dl = fields.Binary('File', readonly=True)
    file_dl_name = fields.Char()
    is_dl_right_now = fields.Boolean(default=True,string=u'Download check file ngay không cần lưu file')
    # có thể xóa
    title_row_for_import = fields.Integer()
    # Download biên bản
    font_height =fields.Integer(default=12,string=u'Font height table')
    font_height_another =fields.Integer(default=12,string=u'Font height khác')
    is_set_tt_col =  fields.Boolean(string=u'Có cột tình trạng?')
    is_not_show_y_kien_ld =  fields.Boolean(string=u'Không thêm dòng ý kiến lãnh đạo')
    empty_ghi_chu_in_bb =  fields.Boolean(string=u'Tự ghi chú trong BB excel')
    
    # Return
    ten_truoc_huy = fields.Char(string=u'Tên trước  hủy',copy=False)
    origin_pick_id = fields.Many2one('stock.picking',string=u'Điều chuyển nguồn')
    loai_tra_hay_chuyen_tiep = fields.Selection([('tra_do_huy',u'Trả do hủy'),('tra_do_muon',u'Trả do mượn'),('chuyen_tiep',u'Chuyển tiếp')],string=u'Loại trả hay chuyển tiếp')
    is_quyen_chuyen_tiep =  fields.Boolean(compute='is_quyen_chuyen_tiep_')
    @api.one
    def is_quyen_huy_bb_(self):
        self.is_quyen_huy_bb = self.user_has_groups('base.group_erp_manager') or (self.env.user == self.create_uid)
        
    
    is_quyen_huy_bb =  fields.Boolean(compute='is_quyen_huy_bb_')
    @api.one
    def is_quyen_chuyen_tiep_(self):
        self.is_quyen_chuyen_tiep = self.user_has_groups('base.group_erp_manager') or (self.env.user.department_id == self.location_dest_id.department_id)
    
    #pdf
    is_chia_2_dong =  fields.Boolean(string=u'Có chia hai dòng không?')
    # filter
    product_id_for_search =  fields.Many2one('product.product',related='move_line_ids.product_id')
    
    #Những hàm ghi đè
    #default, #default_get
    @api.model
    def default_get(self,fields):
        default_location_id = self.env.user.department_id.default_location_id.id
        default_dest_location_id = self.env.user.department_id.default_location_running_id.id

        rs = super(StockPicking, self).default_get(fields)
        rs['location_id'] = default_location_id
        rs['location_dest_id'] =default_dest_location_id
        return rs
    #depends
    #  compute show_validate theo is_validate_mode
    @api.multi
    @api.depends('state', 'is_locked','location_id','location_dest_id')
    def _compute_show_validate(self):
        for picking in self:
            if picking.is_validate_mode:
                show_validate = False
                if picking.is_same_department :
                    if (self.env.user.department_id ==picking.location_id.department_id or self.env.user.department_id ==picking.location_dest_id.department_id) :
                        if self._context.get('planned_picking') and picking.state == 'draft':
                            show_validate = False
                        elif picking.state not in ('draft', 'confirmed', 'assigned') or not picking.is_locked:
                            show_validate = False
                        else:
                            show_validate = True
                else:
                    is_ban_la_ben_nhan = self.env.user.department_id == picking.location_dest_id.department_id
                    show_validate = False
                    if is_ban_la_ben_nhan or self.user_has_groups('base.group_erp_manager'):
                        if picking.state =='done_ben_giao':
                            show_validate = True
                        else:
                            show_validate = False
            else:
                if self._context.get('planned_picking') and picking.state == 'draft':
                    show_validate = False
                elif picking.state not in ('draft', 'confirmed', 'assigned') or not picking.is_locked:
                    show_validate = False
                else:
                    show_validate = True
            picking.show_validate = show_validate
            
    #onchange
    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        pass
    #button
    @api.multi
    def action_confirm(self):
        self.ghom_stock_move_lines()
        self.mapped('move_lines')\
            .filtered(lambda move: move.state == 'draft' or move.state == 'cancel')\
            ._action_confirm()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
            .mapped('move_lines')._action_assign()
        if self.env.context.get('planned_picking') and len(self) == 1:
            action = self.env.ref('stock.action_picking_form')
            result = action.read()[0]
            result['res_id'] = self.id
            result['context'] = {
                'search_default_picking_type_id': [self.picking_type_id.id],
                'default_picking_type_id': self.picking_type_id.id,
                'contact_display': 'partner_address',
                'planned_picking': False,
            }
            return result
        else:
            return True
    #create,write,
    
    @api.model
    def create(self,vals):
        print ('**vals***',vals)
        obj = super(StockPicking, self).create(vals)
        return obj
    @api.multi
    def write(self, vals):
        print ('_____________vals***',vals.get('move_lines'),vals)
        if self.state =='done':
            self = self.with_context(bypass_reservation_update=True)
            move_line_ids =  vals.get('move_line_ids')
            if move_line_ids:
                for ml in move_line_ids:
                    if ml[0]==0:
                        raise UserError (u'Bạn không được tạo mới dòng điều chuyển khi đã hoàn tất biên bản')
        res = super(StockPicking, self).write(vals)
        return res
    #field_view_get
    
    
    def domain_for_location(self,res,doc,location_id='location_id',exclude_location_names = (u'Đối tác nhận',u'Điều chỉnh giảm')):
        doi_tac_nhan_list = self.env['stock.location'].search([('name','in',exclude_location_names)]).mapped('id')
        domain_exclude = "('id','not in',%s)"%(tuple(doi_tac_nhan_list),)
        if self.user_has_groups('base.group_erp_manager'):
            domain = "[('is_kho_cha','=',True),%s]"%domain_exclude
        else:
            domain = "['|',('cho_phep_khac_tram_chon','=', True),'&',('is_kho_cha','=',True),('department_id','=', department_id),%s]"%domain_exclude
        
        nodes =  doc.xpath("//field[@name='%s']"%location_id)
        if len(nodes):
            node = nodes[0]
            node.set('domain',domain )
            
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ['form']:
            doc = etree.XML(res['arch'])
            self.domain_for_location(res,doc,location_id='location_id',exclude_location_names = (u'Đối tác nhận',u'Điều chỉnh giảm'))
            self.domain_for_location(res,doc,location_id='location_dest_id',exclude_location_names = (u'Đối tác giao',u'Điều chỉnh tăng'))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type =='search':
            doc = etree.fromstring(res['arch'])
            nodes =  doc.xpath("//field[@name='location_id']")
            if nodes:
                node = nodes[0]
                node.addnext(etree.Element('separator', {}))
                department_id = self.env.user.department_id.id
                node.addnext(etree.Element('filter', {'string':'Lọc theo  trạm %s'%self.env.user.department_id.name,'name': 'loc_picking_theo_tram_cua_user', 'domain': "['|',('location_id.department_id','=',%s),('location_dest_id.department_id','=',%s)]"%(department_id,department_id)}))
                res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    
    # Hàm phục vụ cho việc ghi đè
    
    @api.multi
    def ghom_stock_move_lines(self):
        """Changes picking state to done by processing the Stock Moves of the Picking
        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        # TDE FIXME: draft -> automatically done, if waiting ?? CLEAR ME
#         todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            print ('**pick.move_line_ids',pick.move_line_ids)
             
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id) 
                print ('moves',moves,'ops',ops)
#                 raise ValueError('kakaka')
                if moves: #could search move that needs it the most (that has some quantities left)
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                   })
                    ops.move_id = new_move.id
    
    # Những hàm mới
    
    
    
    
    #for test
    @api.onchange('categ_id')  
    def categ_id_(self):
            for c,ml in enumerate(self.move_line_ids):
                ml.categ_id = self.categ_id
    
    @api.onchange('location_id')
    def doi_tac_giao_id_(self):
        self.doi_tac_giao_id = self.location_id.partner_id_of_stock_for_report
    @api.onchange('location_dest_id')
    def doi_tac_nhan_id_(self):
        self.doi_tac_nhan_id = self.location_dest_id.partner_id_of_stock_for_report
    
    
    @api.onchange('location_dest_id')
    def location_dest_id_oc_(self):
        print ('self.move_line_ids',self.move_line_ids)
        for ml in self.move_line_ids:
            ml.location_dest_id= self.location_dest_id
  
    @api.onchange('texttemplate_id')
    def onchage_for_ly_do(self):
        if self.texttemplate_id:
            self.ly_do = self.texttemplate_id.name   
    
    #### Button ###########
    @api.multi
    def download_xl_bbbg(self):
        self.ghom_stock_move_lines()
        if self.is_dl_right_now:
            return {
             'type' : 'ir.actions.act_url',
#              'url': '/web/binary/download_xl_bbbg?model=stock.picking&id=%s'%(self.id),
             'url': '/web/binary/download_model/tonkho?download_model=stock.picking&download_model_id=%s&download_key=%s'%(self.id,'write_xl_bb'),
             'target': 'new',
             }
        dl_obj = self
        workbook,name = write_xl_bb (dl_obj)
        
        with contextlib.closing(io.BytesIO()) as buf:
            workbook.save(buf)
            out = base64.encodestring(buf.getvalue())
        self.write({ 'file_dl': out, 'file_dl_name': name})
    
    @api.multi
    def import_file(self):
        importthuvien(self,
                       key=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',
                       key_tram='sml')


    @api.multi
    def check_file(self):
        if self.is_dl_right_now:
            return {
             'type' : 'ir.actions.act_url',
#              'url': '/web/binary/download_checked_import_sml_file?model=stock.picking&id=%s'%(self.id),
             'url': '/web/binary/download_model/tonkho?download_model=stock.picking&download_model_id=%s&download_key=%s'%(self.id,'check_imported_file_sml'),
             'target': 'new',
             }
        dl_obj = self
        workbook,name = check_imported_file_sml(dl_obj)
        with contextlib.closing(io.BytesIO()) as buf:
            workbook.save(buf)
            out = base64.encodestring(buf.getvalue())
        self.write({ 'file_dl': out, 'file_dl_name': name})
    
    @api.multi
    def validate_cua_ben_giao(self):
        self.state = 'done_ben_giao'
        
    ####  ! End button #####
   
    
    # PDF
    @api.multi
    def xem_print(self):
        return {
             'type' : 'ir.actions.act_url',
             'url':'/report/html/tonkho.bao_cao_dieu_chuyen/%s'%self.id,
             'target': 'new',
        }
        
        
    @api.multi
    def xem_print_theo_move_line(self):
        return {
             'type' : 'ir.actions.act_url',
             'url':'/report/html/tonkho.bcdc/%s'%self.id,
             'target': 'new',
        }
    @api.multi
    def xem_print_pdf(self):
        return {
            'type' : 'ir.actions.act_url',
            'url':'/report/pdf/tonkho.bcdc/%s'%self.id,
            'target': 'new',
        }
    def ban_giao_or_nghiem_thu_show(self):
        adict = {u'BBBG':u'Bàn Giao',u'BBNT':u'Nghiệm Thu'}
        if self.ban_giao_or_nghiem_thu != False:
            return adict[self.ban_giao_or_nghiem_thu]
        else:
            return False
    
    
  
   
    
    def generate_partner_bootstrap_ti_le_old(self):
        is_chia_2_dong = True
        row_3_dong = []
        
        alist_1row = []
        alist_1row.append((u'Bên giao',self.source_member_ids[0].name if self.source_member_ids else ''))
        if self.ben_thu_3_ids:
            alist_1row.append((self.title_ben_thu_3.name,self.ben_thu_3_ids[0].name))
        alist_1row.append((u'Bên nhận',self.dest_member_ids[0].name if self.dest_member_ids else ''))
        if self.ben_thu_4_ids:
            alist_1row.append((self.title_ben_thu_4.name, self.ben_thu_4_ids[0].name))
        return alist_1row
    def generate_partner_bootstrap_ti_le(self):
        is_chia_2_dong = self.is_chia_2_dong
        row_3_dong = []
        
        alist_1st_row = []
        alist_2nd_row_new = []
        alist_3rd_row = []
        if is_chia_2_dong:
            alist_2row = alist_2nd_row_new
        else:
            alist_2row =  alist_1st_row
        alist_1st_row.append((u'Bên giao',self.source_member_ids.mapped('name') if self.source_member_ids else ''))
        if self.title_ben_thu_3:
            alist_2row.append((self.title_ben_thu_3.name,[self.ben_thu_3_ids[0].name]))
        alist_1st_row.append((u'Bên nhận',self.dest_member_ids.mapped('name') if self.dest_member_ids else ''))
        if self.title_ben_thu_4:
            alist_2row.append((self.title_ben_thu_4.name, [self.ben_thu_4_ids[0].name]))
        if self.lanh_dao_id:
            alist_3rd_row.append((u'Ý kiến lãnh đạo', [self.lanh_dao_id.name]))
        row_3_dong.append(alist_1st_row)
        if is_chia_2_dong and alist_2nd_row_new:
            row_3_dong.append(alist_2nd_row_new)
        if self.lanh_dao_id:
            row_3_dong.append(alist_3rd_row)
        return row_3_dong
    
    
    
               
                
    
    

    