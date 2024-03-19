from odoo import _
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.http import request

from ..datamodels.commission_response import CommissionResponse


class CommissionServices(Component):
    _inherit = 'base.rest.service'
    _name = 'commission.services'
    _usage = 'commission'
    _collection = 'taxi.services'

    @restapi.method([(['/vtc'], 'POST')], auth='jwt_odoo', type='json', website=False, input_param=Datamodel('driver.info'), output_param=Datamodel('commission.response'))
    def get(self, driver):
        sale_order_id = request.env['sale.order'].sudo().search([('opportunity_id', '=', driver.opportunity_id),
                                                                 ('opportunity_id.stage_id', '=', driver.stage_id),
                                                                 ('opportunity_id.role_id.vehicle_id.driver_id',
                                                                  '=', driver.driver_id),
                                                                 ])
        if sale_order_id and sale_order_id.opportunity_id and sale_order_id.order_line[0].qty_delivered == driver.distance_done:
            opportunity_id = sale_order_id.opportunity_id
            commission_driver = sale_order_id.amount_total - sale_order_id.commission
            description = _('Description journey - Pick up zone: %s - Destination zone: %s - the [%s] %s') % (
                opportunity_id.pick_up_zone_id.name if opportunity_id.pick_up_zone_id else opportunity_id.pick_up_zone,
                opportunity_id.destination_zone_id.name if opportunity_id.destination_zone_id else opportunity_id.destination_zone,
                opportunity_id.pick_up_datetime.strftime('%d/%m/%Y, %H:%M:%S'),
                opportunity_id.client_note)
            return CommissionResponse(commission_driver=commission_driver, opportunity_id=opportunity_id, description_journey=description)
        else:
            return CommissionResponse(commission_driver=0, opportunity_id=0, description_journey='')
