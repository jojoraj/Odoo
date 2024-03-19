from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class DriverCore(Datamodel):
    _name = 'driver.core'

    driver_phone = fields.String(allow_none=False, required=True)


class DriverInfo(Datamodel):
    _name = 'driver.info'
    _inherit = 'driver.core'

    driver_id = fields.Integer(allow_none=False, required=True)
    opportunity_id = fields.Integer(allow_none=False, required=True)
    distance_done = fields.Float(allow_none=False, required=True)
    stage_id = fields.Integer(allow_none=False, required=True)
