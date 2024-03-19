from geopy.geocoders import Nominatim
from odoo import api, fields, models

AGENT = 't.rakotoarisoa@etechconsulting-mg.com'


def get_point_coordinate(address):
    geolocator = Nominatim(user_agent=AGENT)
    location = geolocator.geocode(address)
    result = {'longitude': location.logitude, 'latitude': location.latitude, 'address': location.address}
    return result


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

    @api.onchange('pickup_point')
    def onchange_pickup_point(self):
        if not self.pickup_point:
            return
        location = get_point_coordinate(self.pickup_point)
        if location:
            location.get('address')
            self.long_pickup_point = location.get('longitude')
            self.lat_pickup_point = location.get('latitude')

    @api.onchange('storage_point')
    def onchange_storage_point(self):
        if not self.storage_point:
            return
        storage = get_point_coordinate(self.storage_point)
        storage.get('address')
        if storage:
            self.long_storage_point = storage.get('longitude')
            self.lat_storage_point = storage.get('latitude')
