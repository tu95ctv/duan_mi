# -*- coding: utf-8 -*-
from odoo import http

# class Tkbd(http.Controller):
#     @http.route('/tkbd/tkbd/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tkbd/tkbd/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tkbd.listing', {
#             'root': '/tkbd/tkbd',
#             'objects': http.request.env['tkbd.tkbd'].search([]),
#         })

#     @http.route('/tkbd/tkbd/objects/<model("tkbd.tkbd"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tkbd.object', {
#             'object': obj
#         })