from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class DefaultResponse(Datamodel):
    _name = 'default.response'

    status_code = fields.Integer(required=True)
    data = fields.Dict()
    message = fields.String()
