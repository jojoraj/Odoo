from odoo import SUPERUSER_ID
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.http import request

from ..datamodels.default_response import DefaultResponse


class TripServices(Component):
    _inherit = 'base.rest.service'
    _name = 'trip.services'
    _usage = 'trip'
    _collection = 'taxi.services'

    @restapi.method([(['/status'], 'PUT')], type='json', auth='none', website=False, input_param=Datamodel('trip.status'), output_param=Datamodel('default.response'))
    def set_trip_status(self, trip_status):
        lead_id = request.env['crm.lead'].sudo().search([('siid', '=', trip_status.siid)])
        stage = {
            'pending': request.env.ref('crm.stage_lead1'),
            'accepted': request.env.ref('crm.stage_lead2'),
            'pick_up_client': request.env.ref('evtc_taxi.stage_pick_up_client'),
            'in_progress': request.env.ref('crm.stage_lead3')
        }
        stage_id = stage.get(trip_status.status.lower(), None)
        if stage_id and lead_id:
            try:
                if lead_id.stage_id == stage_id:
                    return DefaultResponse(status_code=202, data=trip_status.dump(), message=f'Status already : {trip_status.status}')
                if trip_status.status.lower() == 'accepted' and trip_status.driver_phone:
                    plannings = request.env['auto.planning.wizard']
                    plannings.automatic_assignment(lead_id.id, trip_status.driver_phone)
                    return DefaultResponse(status_code=201, data=trip_status.dump(), message='Status changed')
                values = {'stage_id': stage_id.id}
                if trip_status.pickup_tracking_id:
                    values.update({'tracking_id_map': trip_status.pickup_tracking_id})
                lead_id.with_user(SUPERUSER_ID).write(values)
                return DefaultResponse(status_code=201, data=trip_status.dump(), message='Status changed')
            except Exception as e:
                return DefaultResponse(status_code=500, data={'description': e}, message='Internal servor error')
        return DefaultResponse(status_code=404, message='Ressource not found')
