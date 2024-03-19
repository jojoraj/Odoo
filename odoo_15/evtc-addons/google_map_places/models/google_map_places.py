from odoo import fields, models


class GoogleMapPlacesCategory(models.Model):
    _name = 'google.map.places.category'
    _description = 'Google map places category'

    active = fields.Boolean()
    name = fields.Char()


class GoogleMapPlaces(models.Model):
    _name = 'google.map.places'
    _description = 'Google map places'

    active = fields.Boolean()
    name = fields.Char(required=True)
    places_category_id = fields.Many2one('google.map.places.category', 'Category')
    use = fields.Boolean()
