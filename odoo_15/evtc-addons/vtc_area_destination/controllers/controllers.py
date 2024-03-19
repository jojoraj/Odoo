from odoo import _, http
from odoo.http import request


class EvtcAreaDestination(http.Controller):

    @http.route('/destination/area/wait/time', auth='public', type='json')
    def list_time_waite(self, **kw):
        area_time = request.env['area.time.wait'].sudo().search([('active', '=', True)])
        to_show = area_time and [{
            'id': area.id,
            'name': area.real_time,
            'price': area.waiting_price,
            'is_selected': False,
            'minutes': area.wait_time_mn,
        } for area in area_time] or [{'id': 0, 'name': _('No wait time'), 'price': 0}]

        return to_show
