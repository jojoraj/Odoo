import re
from datetime import datetime

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.http import request

from ..datamodels.payment_info import PaymentResult
from ..datamodels.sale_order_history import SaleOrderHistory


class HistoryServices(Component):
    _inherit = 'base.rest.service'
    _name = 'history.services'
    _usage = 'taxi'
    _collection = 'taxi.services'
    _default_auth = 'jwt_odoo'

    @restapi.method([(['/history/<string:driver_phone>'], 'GET')],
                    type='json', auth='keycloak', website=False, output_param=Datamodel('sale.order.history', is_list=True))
    def get_history(self, driver_phone):
        from_date = request.params.get('fromDate', False)
        to_date = request.params.get('toDate', False)
        phone = re.sub(r'\D+', '', driver_phone)
        domain = [
            ('state', '=', 'sale'),
            ('referrer_id', '!=', False),
            ('reference_code', '!=', False)
        ]
        if from_date:
            from_date = datetime.strptime(f'{from_date} 00:00:00', '%Y-%m-%d %H:%M:%S')
            domain.append(('pick_up_datetime', '>=', from_date))
        if to_date:
            to_date = datetime.strptime(f'{to_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            domain.append(('order_stop_date', '<=', to_date))
        order_ids = request.env['sale.order'].sudo().search(domain, order='pick_up_datetime desc').filtered(
            lambda item: re.sub(r'\D+', '', item.referrer_id.phone) == phone)
        values = list()
        for order in order_ids:
            history = SaleOrderHistory(
                reference=order.reference_code,
                pickup_zone=order.pick_up_zone or '',
                destination_zone=order.destination_zone or '',
                distance_done=order.real_distance,
                duration=f'{int(order.duration)}:{int((order.duration * 60) % 60)}',
                start_date=order.pick_up_datetime.isoformat() if order.pick_up_datetime else None,
                stop_date=order.order_stop_date.isoformat() if order.order_stop_date else None,
                amount_total=order.amount_total,
                commission=order.commission)
            values.append(history)
        return values

    @restapi.method([(['/payment'], 'POST')], type='json', auth='keycloak', input_param=Datamodel('payment.info'), output_param=Datamodel('payment.result'))
    def post_payment(self, payment_infos):
        opportunity_id = request.env['crm.lead'].sudo().search([('siid', '=', payment_infos.siid)])
        if opportunity_id:
            if payment_infos.length:
                amount = opportunity_id.process_order(payment_infos.length)
                return PaymentResult(siid=payment_infos.siid, amount_total=str(amount))
            else:
                opportunity_id.confirm_order()
                return PaymentResult(siid=payment_infos.siid, status=200)
        return PaymentResult(siid=payment_infos.siid, status=500)
