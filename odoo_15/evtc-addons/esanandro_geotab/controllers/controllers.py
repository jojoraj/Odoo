from odoo import http
from odoo.http import request


class Geotab(http.Controller):

    @http.route('/web/geotab-check-point', type='json', website=True, sitemap=False, auth='public')
    def geotab_check_point(self, data=None, **kw):
        if data:
            vals = request.env['esanandro.geotab'].sudo().suggest_address_geopy(data)
            if vals:
                values = vals.get('address')
                return values.split(',')
        return []

    @http.route('/web/vehicle-related-tarif', type='json', website=True, sitemap=False, auth='public')
    def vehicle_related_tarif(self, reservation_id=None, **kw):
        reserv = []
        if not reservation_id:
            return reserv
        vehicle = request.env['esanandro_geotab.reservation'].sudo().get_all_vehicle_on_tarif(int(reservation_id))
        if vehicle:
            reserv += vehicle
        return reserv

    @http.route('/web/get-coordonate-description', type='json', website=True, sitemap=False, auth='public')
    def get_coordinate_description(self, coordinate=None, **kw):
        if not coordinate:
            return []
        pickup, storage = coordinate
        points = request.env['esanandro_geotab.reservation'].sudo().get_reservation_information(pickup, storage)
        if points:
            return points
        return []

    @http.route('/web/geotab/marker', type='json', website=True, sitemap=False, auth='public')
    def make_marker(self, address=None, **kw):
        if address:
            vals = request.env['esanandro_geotab.reservation'].sudo().get_point_lat_long(address)
            if vals:
                return vals[0]
        return {}

    @http.route('/web/geotab/waypoint', type='json', website=True, sitemap=False, auth='public')
    def get_waypoint(self, address=None, **kw):
        if address:
            vals = request.env['esanandro_geotab.reservation'].sudo().get_models_way_point(address)
            if vals:
                return vals[0]
        return {}
