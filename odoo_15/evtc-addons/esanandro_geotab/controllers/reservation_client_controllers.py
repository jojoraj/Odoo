from datetime import datetime, timedelta

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import Controller, request, route


class EsanandroReservation(Controller):

    @route('/web/esanandro/geotab/reservation', type='http', website=True, sitemap=False, auth='user')
    def esanandro_geotab_reservation(self, *args, **kwargs):
        ensure_db()
        values = {}
        partner_id = request.env.user.partner_id.id
        driver_id = request.env['esanandro_geotab.reservation'].search(
            [('fleet_vehicle_id.driver_id', '=', partner_id)], order="date_from DESC")
        client_reserv = request.env['esanandro_geotab.reservation'].search([('partner_id', '=', partner_id)],
                                                                           order="date_from DESC")
        if driver_id:
            values.update({'client_role': 'driver_id', 'data': driver_id})
        else:
            values.update({'client_role': 'client_id', 'data': client_reserv})

        return request.render("esanandro_geotab.reservation_client_frontend_common", values)

    @route('/web/vehicle-create', type='http', website=True, sitemap=False, auth='user')
    def create_reservation(self, data=None, *args, **kwargs):
        def get_name_reserv(rec):
            nb = request.env['crm.lead'].search_count([])
            return f"reserv n° {str(nb).zfill(5)}"

        data = kwargs
        time = ' '.join(data['my_datetimepicker'].split(' ')[:-1])
        val = datetime.strptime(time, '%m/%d/%Y %H:%M')
        h, m, s = data['duration_trip'].split(':')
        t = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        seconds = t.seconds
        minutes = seconds / 3600
        kilometers = data['kilometers'].split(' ')[0]
        opportunity = {
            'partner_id': request.env.user.partner_id.id,
            'name': get_name_reserv(self),
            'pick_up_datetime': val,
            'destination_zone': data['pick_back_zone'],
            'pick_up_zone': data['pickup_zone'],
            'client_note': data['note'],
            'duration': minutes,
            'estimated_kilometers': kilometers
        }
        request.env['crm.lead'].sudo().create(opportunity)
        values = {
            'status': True,
            'message': "Vos informations à bien été enregistrer"
        }
        return request.render("esanandro_geotab.reservation_client_frontend_common", values)

    @route('/web/geotab/new/latLng', type='json', website=True, sitemap=False, auth='user')
    def new_record_address(self, latLng=None):
        latLng = latLng and latLng or {}
        return request.env['esanandro_geotab.reservation'].sudo().get_new_adress_with_latLng(
            latLng) if latLng else "Unknown adress"
