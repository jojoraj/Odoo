from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class TripStatus(Datamodel):
    _name = 'trip.status'

    siid = fields.String(required=True)
    status = fields.String(required=True)
    pickup_tracking_id = fields.String(required=False)
    driver_phone = fields.String()
