from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderHistory(Datamodel):
    _name = 'sale.order.history'

    reference = fields.String()
    pickup_zone = fields.String()
    destination_zone = fields.String()
    distance_done = fields.Float()
    duration = fields.String()
    start_date = fields.DateTime(allow_none=True)
    stop_date = fields.DateTime(allow_none=True)
    amount_total = fields.Float()
    commission = fields.Float()
