# -*- coding: utf-8 -*-
from odoo import http

# class Hcmaccount(http.Controller):
#     @http.route('/hcmaccount/hcmaccount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hcmaccount/hcmaccount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hcmaccount.listing', {
#             'root': '/hcmaccount/hcmaccount',
#             'objects': http.request.env['hcmaccount.hcmaccount'].search([]),
#         })

#     @http.route('/hcmaccount/hcmaccount/objects/<model("hcmaccount.hcmaccount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hcmaccount.object', {
#             'object': obj
#         })