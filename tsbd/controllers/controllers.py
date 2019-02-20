# -*- coding: utf-8 -*-
from odoo import http

# class Tsbd(http.Controller):
#     @http.route('/tsbd/tsbd/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsbd/tsbd/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsbd.listing', {
#             'root': '/tsbd/tsbd',
#             'objects': http.request.env['tsbd.tsbd'].search([]),
#         })

#     @http.route('/tsbd/tsbd/objects/<model("tsbd.tsbd"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsbd.object', {
#             'object': obj
#         })