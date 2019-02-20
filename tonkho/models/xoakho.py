# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"
#     def unlink(self):
#             precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#             for ml in self:
# #                 if ml.state in ('done', 'cancel'):
# #                     raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
#                 # Unlinking a move line should unreserve.
#                 if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
#                     try:
#                         self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
#                     except UserError:
#                         if ml.lot_id:
#                             self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
#                         else:
#                             raise
#             moves = self.mapped('move_id')
#             res = super(StockMoveLine, self).unlink()
#             if moves:
#                 moves._recompute_state()
#             return res
#     
#     
#     
#     
# class StockMove(models.Model):
#     _inherit = "stock.move"
#     
#     def unlink(self):
# #         if any(move.state not in ('draft', 'cancel') for move in self):
# #             raise UserError(_('You can only delete draft moves.'))
#         self.mapped('move_line_ids').unlink()
#         return super(StockMove, self).unlink()
class XoaKho(models.TransientModel):
    _name = 'tonkho.xoakho'
    @api.multi
    def xoakho_action(self):
        for model_name in ['stock.quant','stock.production.lot','stock.inventory',]:#'stock.move','stock_move','product_product,'stock.picking'
            print ('xoa %s'%model_name)
            self.env[model_name].search([]).unlink()
            
    def xoa_stock_move(self):
        for model_name in ['stock.move']:#'stock.move','stock_move','product_product,'stock.picking'
            print ('xoa %s'%model_name)
            self.env[model_name].search([]).unlink()
    def xoa_stock_move_line(self):
        for model_name in ['stock.move.line']:#'stock.move','stock_move','product_product,'stock.picking'
            print ('xoa %s'%model_name)
            self.env[model_name].search([]).unlink()
    def xoa_stock_picking(self):
        for model_name in ['stock.picking']:#'stock.move','stock_move','product_product,'stock.picking'
            print ('xoa %s'%model_name)
            self.env[model_name].search([]).unlink()
    def xoa_product_template(self):
        for model_name in ['product.template']:#'stock.move','stock_move','product_product,'stock.picking'
            print ('xoa %s'%model_name)
            self.env[model_name].search([]).unlink()
                   
            
            
            # xoa theo thu tu sau o phppgadmin, stock_move, stock_move_line,stock_picking,(product_template-->product_product)
            

     
        
        