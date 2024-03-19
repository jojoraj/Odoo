from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class DefaultResponse(Datamodel):
    _name = 'res.default'

    status_code = fields.Integer(required=True)
    message = fields.String()
