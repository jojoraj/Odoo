from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class TripInfos(Datamodel):
    _name = 'trip.infos'

    siid = fields.String(allow_none=True)
    opportunity = fields.Dict(allow_none=True)
    orders = fields.Dict(allow_none=True)
    api_key = fields.String(allow_none=True, required=True)