from odoo import http
from odoo.addons.evtc_front.controllers.controllers import EvtcFront
from odoo.http import request


class EvtcLocation(EvtcFront):

    # long duration
    @http.route('/long-duration', auth='user', website="True")
    def evtc_reservation_long(self, **kw):
        price_location_ids = http.request.env['price.location'].sudo().search([])
        list_price_ids = http.request.env['fleet.vehicle.price.category'].sudo().search([('is_location', '=', True),
                                                                                         ('vehicle_location_id.id', 'in', price_location_ids.ids)])

        vehicle_category_ids = http.request.env['fleet.vehicle.model.category'].sudo().search([('list_price.id', 'in', list_price_ids.ids)])

        favorite_address = http.request.env.user.partner_id.child_ids.filtered(
            lambda x: x.type == 'other' and x.is_favorites)
        child_ids = http.request.env.user.partner_id.child_ids
        historic = child_ids.filtered(lambda x: x.type == 'other' and x.is_historical).sorted(lambda c: c.create_date, reverse=True)[:6]
        google_api_keys = request.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        groups_user = request.env.user.has_group('evtc_front.reservation_for_others')
        historic_address_to_show = historic[-6:] if historic else []
        values = {
            'vehicle_category_ids': vehicle_category_ids,
            'favorite_address': favorite_address,
            'historic': historic,
            'google_maps_api_key': google_api_keys,
            'user_access': groups_user, 
            'countries': request.env['res.country'].sudo().search([]),
            'partner': request.env.user.partner_id or None
        }
        return http.request.render("evtc_location.long_duration_index_long", values)

    @http.route(['/price/location'], type='json', auth='user', website=True)
    def render_price_location(self, **kwargs):
        vehicle_id = int(kwargs.get('id', False))
        vehicle_category_id = request.env['fleet.vehicle.model.category'].sudo().search([('id', '=', vehicle_id)])
        list_data = []
        if vehicle_category_id:
            vehicle_location_ids = vehicle_category_id.list_price.filtered(
                lambda v: v.is_location and v.vehicle_location_id).mapped('vehicle_location_id')
            for rec in vehicle_location_ids:
                list_data.append({
                    'id': rec.id,
                    'name': rec.name,
                    'hours': rec.hours,
                    'price': rec.price,
                })
            return list_data
        else:
            return False
