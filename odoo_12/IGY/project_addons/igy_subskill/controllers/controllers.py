# -*- coding: utf-8 -*-
from odoo import http

# class IgyBadge(http.Controller):
#     @http.route('/igy_badge/igy_badge/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/igy_badge/igy_badge/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('igy_badge.listing', {
#             'root': '/igy_badge/igy_badge',
#             'objects': http.request.env['igy_badge.igy_badge'].search([]),
#         })

#     @http.route('/igy_badge/igy_badge/objects/<model("igy_badge.igy_badge"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('igy_badge.object', {
#             'object': obj
#         })