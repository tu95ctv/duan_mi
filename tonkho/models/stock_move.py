# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"
    ghi_chu = fields.Char()
#     def _action_done(self):
#         print ('***_action_done')
#         return super(StockMove, self.with_context(stt=self.stt))._action_done()
    
#     def choose_ghi_chu(self):
#         if  len(self.move_line_ids)==1:
#             
#         notempty_ghi_chu_in_ml_ids = set(self.move_line_ids.filtered(lambda r: r.ghi_chu).mapped('ghi_chu'))
#         if not notempty_ghi_chu_in_ml_ids:
#             merge = True
#             ghi_chu = self.ghi_chu
#         else:
#             merge = False
#             ghi_chu = ml.ghi_chu or self.ghi_chu
#             if len(notempty_ghi_chu_in_ml_ids) ==1:
#                 merge = True
                
    
#     def ghi_chu_theo_move_line_ids_(self):
#         rs= True if self.move_line_ids.filtered(lambda r:bool(r.ghi_chu)) else False
# #         print (self.product_id.name,rs, self.move_line_ids.mapped('ghi_chu'))
#         return rs
#     def colspan_(self,has_serial_number):
#         print ('has_serial_number***',has_serial_number)
#         has_serial_number = 3 if has_serial_number else 1 # co tinh trang
#         ghi_chu_move_lines_ids = self.ghi_chu_theo_move_line_ids_()
#         ghi_chu_move_lines_ids = 1 if ghi_chu_move_lines_ids else 0
#         val = ghi_chu_move_lines_ids + has_serial_number
#         print (self.product_id.name,'val********',val,has_serial_number,ghi_chu_move_lines_ids)
#         return val
        
#     def action_show_details(self):
#         """ Returns an action that will open a form view (in a popup) allowing to work on all the
#         move lines of a particular move. This form view is used when "show operations" is not
#         checked on the picking type.
#         """
#         self.ensure_one()
# 
#         # If "show suggestions" is not checked on the picking type, we have to filter out the
#         # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
#         # different views to display one field or another so that the webclient doesn't have to
#         # fetch both.
#         if self.picking_id.picking_type_id.show_reserved:
#             view = self.env.ref('stock.view_stock_move_operations')
#         else:
#             view = self.env.ref('stock.view_stock_move_nosuggest_operations')
#         show_lots_m2o=self.has_tracking != 'none' and (self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
#         print ("self.has_tracking != 'none' ",self.has_tracking != 'none' )
#         print ("self.picking_type_id.use_existing_lots",self.picking_type_id.use_existing_lots)
#         print ("self.origin_returned_move_id.id",self.origin_returned_move_id.id)
#         print ('show_lots_m2o',show_lots_m2o)
#         return {
#             'name': _('Detailed Operations'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'stock.move',
#             'views': [(view.id, 'form')],
#             'view_id': view.id,
#             'target': 'new',
#             'res_id': self.id,
#             'context': dict(
#                 self.env.context,
#                 show_lots_m2o=self.has_tracking != 'none' and (self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
#                 show_lots_text=self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
#                 show_source_location=self.location_id.child_ids,
#                 show_destination_location=self.location_dest_id.child_ids,
#                 show_package=not self.location_id.usage == 'supplier',
#                 show_reserved_quantity=self.state != 'done'
#             ),
#         }
        
        
    
#     def _action_cancel(self):
#         if any(move.state == 'done' for move in self):
#             raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
#         for move in self:
#             if move.state == 'cancel':
#                 continue
# #             move._do_unreserve()
#             siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
#             if move.propagate:
#                 # only cancel the next move if all my siblings are also cancelled
#                 if all(state == 'cancel' for state in siblings_states):
#                     move.move_dest_ids._action_cancel()
#             else:
#                 if all(state in ('done', 'cancel') for state in siblings_states):
#                     move.move_dest_ids.write({'procure_method': 'make_to_stock'})
#                     move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
#         self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
#         return True
        
        
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'search_move_line_in_write' in self._context:# de lam gì?
            return False
        return super(StockMove,self).search(args, offset, limit, order, count=count)
    

