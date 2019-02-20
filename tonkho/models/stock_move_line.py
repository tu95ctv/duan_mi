# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero,_float_check_precision,float_round,float_compare
from odoo.exceptions import UserError,ValidationError
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    stock_quant_id = fields.Many2one('stock.quant', string=u"Lấy vật tư có trong kho")
    tracking = fields.Boolean(string=u'Có SN hay không', store=False,compute='tracking_')
    @api.depends('product_id.tracking')
    def tracking_(self):
        for r in self:
            r.tracking = r.product_id.tracking == 'serial'
        
    stt = fields.Integer()
    sltk = fields.Integer(compute='sltk_',store=True)
    @api.depends('product_id','lot_id','location_id')
    def sltk_(self):
        for r in self:
            quants = self.env['stock.quant'].search([('product_id','=',r.product_id.id),\
                                                     ('lot_id','=',r.lot_id.id),('location_id','=',r.location_id.id),('quantity','>',0)])
            if quants:
                r.sltk = quants[0].quantity
                
                
    categ_id = fields.Many2one('product.category',related='product_id.categ_id', store=False,readonly=True)
    thiet_bi_id = fields.Many2one('tonkho.thietbi',related='product_id.thiet_bi_id' ,string = u'Thiết bị',readonly=True)
    ghi_chu = fields.Text(string=u'Ghi chú vật tư')
    inventory_line_id = fields.Many2one('stock.inventory.line')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',related='move_id.inventory_id')
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')], default='tot', string=u'Tình trạng',required=True)
    ref_picking_id_or_inventory_id = fields.Char(compute='ref_picking_id_or_inventory_id_', store=True,string=u'Phiếu tham chiếu')
    
    @api.depends('inventory_id','picking_id.name')
    def ref_picking_id_or_inventory_id_(self):
        for r in self:
            ref = u'INV: ' + r.inventory_id.name  if r.inventory_id else r.picking_id.name
            r.ref_picking_id_or_inventory_id = ref
    pn = fields.Char(related='product_id.pn',store = True,readonly="1")
    #return
    move_line_dest_ids = fields.Many2many(
        'stock.move.line', 'stock_move_line_move_line_rel', 'move_line_orig_id', 'move_line_dest_id', 'Destination Move Lines',
        copy=False,
        help="Optional: next stock move when chaining them")
    move_line_orig_ids = fields.Many2many(
        'stock.move.line', 'stock_move_line_move_line_rel', 'move_line_dest_id', 'move_line_orig_id', 'Original Move Lines',
        copy=False,
        help="Optional: previous stock move when chaining them")
    origin_returned_move_id = fields.Many2one('stock.move.line', 'Origin return move', copy=False, help='Move that created the return move')
    returned_move_ids = fields.One2many('stock.move.line', 'origin_returned_move_id', 'All returned moves', help='Optional: all returned moves created from this move')

    decoration_danger = fields.Boolean(compute='decoration_danger_')
    @api.depends('sltk','location_id','qty_done')
    def decoration_danger_(self):
        for r in self:
            r.decoration_danger = (not r.location_id.cho_phep_khac_tram_chon) and (r.qty_done > r.sltk)

    # hàm ghi đè
    
    @api.one
    @api.depends('picking_id.picking_type_id', 'product_id.tracking')
    def _compute_lots_visible(self):
        self.lots_visible =True
   
    @api.onchange('qty_done')
    def _onchange_qty_done(self):# ghi đè để tránh cảnh báo: You can only process 1.0 Card for products with unique serial number.
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This onchange will warn him if he set `qty_done` to a non-supported value.
        """
        res = {}
        if self.product_id.tracking == 'serial':
#             fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.move_id.product_id.uom_id.rounding)#original
            fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.product_id.uom_id.rounding)
            #original:
            if fl !=0:# fl=1 nếu là băng nhau,-1 nếu khác nhau
            # để tránh cảnh báo: You can only process 1.0 Card for products with unique serial number.
#             if fl > 1:
                message = _('You can only process 1.0 %s for products with unique serial number.') % self.product_id.uom_id.name
                res['warning'] = {'title': _('Warning'), 'message': message}
        return res
    
    def _action_done(self):
        if 'action_done_from_stock_inventory' in self._context:
            self =  self.with_context(update_inventory={'stt':self.stt, 'inventory_line_id':self.inventory_line_id.id})
        return super(StockMoveLine,self )._action_done()
    
        
    # Constrans viết mới
    @api.constrains('product_id','lot_id')
    def pn_id_product_id_(self):
        for r in self:
   
            if r.lot_id:
                if r.lot_id.product_id != r.product_id:
                    raise ValidationError(u'product_id ở lot_id khác với product_id')
                
    @api.constrains('location_id','location_dest_id')
    def location_id_dest_location_id_(self):
        for r in self:
            if r.state =='done':
                if r.location_id ==r.location_dest_id:
                    raise UserError(u'Địa điểm đích và địa điểm nguồn không được giống nhau')
    @api.constrains('state','tinh_trang','ghi_chu')
    def state_tinh_trang_(self):
        for r in self:
            if r.state =='done':
                if r.lot_id:
                    if r.tinh_trang:
                        r.lot_id.tinh_trang = r.tinh_trang
                    if r.ghi_chu:
                        r.lot_id.ghi_chu = r.ghi_chu
        
    # onchange
    @api.onchange('lot_id','product_id')
    def location_id_oc_(self):
        if self.lot_id or self.product_id.id:
            qs = self.env['stock.quant'].search([('location_id', 'child_of',self.picking_id.location_id.id),('lot_id','=',self.lot_id.id),('product_id','=',self.product_id.id),('quantity','>',0)])
            location_ids= qs.mapped('location_id.id')
            rt = {}
            if location_ids:
                location_id = location_ids[0]
                rt = {'value':{'location_id':location_id,
                    }}
            domain ="['|',('id', 'in',%s),'&',('id', 'child_of',parent.location_id),('is_kho_cha', '=',True)]"%(tuple(location_ids),)
            rt.update({
                'domain': {
                        'location_id':domain ,
                }
                    })
            return rt
        else:
            domain =[('id', 'child_of','parent.location_id'),('is_kho_cha', '=',True)]
            return {
                'domain': {
                        'location_id':domain ,
                }
                    }
    @api.onchange('lot_id')
    def lot_id_oc_(self):
        if self.lot_id:
            self.product_id = self.lot_id.product_id
        if self.lot_id.tinh_trang:
            self.tinh_trang = self.lot_id.tinh_trang
    @api.onchange('product_id')
    def product_id_oc_(self):
        if self.product_id:
            pr_id = self.product_id.id
            domain = [('product_id','=',pr_id)]
            sn_ids = self.env['stock.production.lot'].search([('product_id','=',pr_id)])
            if len(sn_ids)==1:
                self.lot_id = sn_ids
            if self.product_id:
                self.qty_done = 1
                self.product_uom_id = self.product_id.uom_id.id   
        else:
            domain = []
        return {
            'domain': {
                    'lot_id':domain ,
            }  
        }
    @api.onchange('stock_quant_id')
    def stock_quant_id_change_(self):
        if self.stock_quant_id:
            self.product_id = self.stock_quant_id.product_id
            self.lot_id = self.stock_quant_id.lot_id
            self.location_id = self.stock_quant_id.location_id

   
        

                