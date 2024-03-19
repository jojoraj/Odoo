from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class CommissionResponse(Datamodel):
    _name = "commission.response"

    commission_driver = fields.Float(required=True)
    opportunity_id = fields.Integer(required=True)
    description_journey = fields.String(required=True)
