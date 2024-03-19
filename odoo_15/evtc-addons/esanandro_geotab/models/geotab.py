from geopy.geocoders import Nominatim
from odoo import fields, models

AGENT = 't.rakotoarisoa@etechconsulting-mg.com'


def get_point_coordinate(address):
    geolocator = Nominatim(user_agent=AGENT)
    location = geolocator.geocode(address)
    if location:
        result = {'longitude': location.longitude, 'latitude': location.latitude, 'address': location.address}
        return result
    else:
        return {}


class Geotab(models.Model):
    _name = 'esanandro.geotab'
    _description = 'My Geotab'

    name = fields.Char()
    pickup_point = fields.Char(string="Point de rammassage")
    storage_point = fields.Char(string="Point de remisage")
    long_pickup_point = fields.Char(string="Longitude point rammassage")
    lat_pickup_point = fields.Char(string="Latitude point remisage")
    long_storage_point = fields.Char(string="longitude point remisage")
    lat_storage_point = fields.Char(string="Latitude point remisage")
    vehicle = fields.Many2one("fleet.vehicle", string=u"véhicule")
    distance_traveled = fields.Float(string="Distance parcourue")
    travel_begin_time = fields.Datetime(string=u"Début du trajet")
    travel_end_time = fields.Datetime(string="Fin du trajet")
    travel_time = fields.Float(string=u"Durée du trajet (mn)")
    travel_cost = fields.Float(string="Cout du trajet")

    def suggest_address_geopy(self, vals):
        if len(list(vals)) > 2:
            location = get_point_coordinate(vals)
            values = {'address': location.get('address', False)}
            return values
        else:
            return {}
