# from odoo import http


# class EvtcBackOffice(http.Controller):
#     @http.route('/evtc_back_office/evtc_back_office/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/evtc_back_office/evtc_back_office/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('evtc_back_office.listing', {
#             'root': '/evtc_back_office/evtc_back_office',
#             'objects': http.request.env['evtc_back_office.evtc_back_office'].search([]),
#         })

#     @http.route('/evtc_back_office/evtc_back_office/objects/<model("evtc_back_office.evtc_back_office"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('evtc_back_office.object', {
#             'object': obj
#         })
