from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class PaymentInfo(Datamodel):
    _name = 'payment.info'

    siid = fields.String(allow_none=False, required=True)
    length = fields.Float(allow_none=False)


class PaymentResult(Datamodel):
    _name = 'payment.result'
    _inherit = 'payment.info'

    amount_total = fields.String(allow_none=False)
    siid = fields.String(allow_none=False, required=True)
    status = fields.Int(allow_none=False)
