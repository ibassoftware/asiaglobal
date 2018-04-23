# -*- coding: utf-8 -*-
from odoo import http

# class Asiaglobal(http.Controller):
#     @http.route('/asiaglobal/asiaglobal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asiaglobal/asiaglobal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asiaglobal.listing', {
#             'root': '/asiaglobal/asiaglobal',
#             'objects': http.request.env['asiaglobal.asiaglobal'].search([]),
#         })

#     @http.route('/asiaglobal/asiaglobal/objects/<model("asiaglobal.asiaglobal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asiaglobal.object', {
#             'object': obj
#         })