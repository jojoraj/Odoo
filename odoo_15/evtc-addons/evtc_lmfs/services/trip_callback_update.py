from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from werkzeug.exceptions import BadRequest
from odoo import _
from odoo.http import request


class OpportunityCallback(Component):
    _inherit = 'base.rest.service'
    _name = 'trip.update'
    _usage = 'trip'
    _collection = 'trip.callbacks'

    def _translate_error_callback_message(self, errors):
        message = _('The following Errors were encountered while updating the data: \n') if errors else ''
        for key in errors:
            message += '%s: %s \n' % (key, errors[key])
        return message
    

    @restapi.method([(['/update'], 'POST')], auth='lmfs_api_key', type='json', website=False,
                    input_param=Datamodel('trip.infos'))
    def update_trip_infos(self, trip_infos):
        opportunity_id = request.env['crm.lead'].sudo().search([
            ('siid', '=', trip_infos.siid)
        ])
        values = {
            "types": "POST",
            "headers": "",
            "response_header": "",
            "response_content": "",
            "request_body": trip_infos,
            "url": "/callbacks/trip/update",
            "name": "update",
            "code": "",
            "content": "content",
            "reason": "",
            "encodings": "",
            "date": "",
            "response": "",
        }
        test = request.env['request.lmfs.log'].create(values)
        if opportunity_id.role_id and opportunity_id.role_id.vehicle_id.geolocalization_type == 'geotab':
            return {
                'status_code': 200,
                'message': _('Vehicle localisation: GEOTAB')
            }
        if not opportunity_id:
            raise BadRequest(_('Ivalid  siid'))
        orders = opportunity_id.order_ids.filtered(lambda s: s.state == 'draft')
        order_id = orders[-1] if len(orders) > 1 else orders
        if not orders and trip_infos.orders:
            raise BadRequest(_('No order found for this trip'))
        request_data = ''
        if trip_infos.opportunity:
            request_data += self._translate_error_callback_message(
                opportunity_id.set_opportunity_request(trip_infos.opportunity)
            )
        if not request_data and trip_infos.orders:
            request_data += self._translate_error_callback_message(
                order_id.set_order_request(trip_infos.orders)
            )
        if request_data:
            raise BadRequest(request_data)
        return {
            'status_code': 200,
        }
