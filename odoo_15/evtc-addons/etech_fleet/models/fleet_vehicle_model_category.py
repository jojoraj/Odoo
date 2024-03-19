# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

import pytz
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from pytz.lazy import LazyDict, LazyList, LazySet  # noqa

class FleetVehicleModelCategory(models.Model):
    _inherit = 'fleet.vehicle.model.category'

    place_number = fields.Integer(string="Nombre de place")
    tarif = fields.Float(string="Tarif au kilomètre")
    minimum_price_id = fields.Many2one('account.minimum.price')
    image = fields.Image()
    list_price = fields.One2many('fleet.vehicle.price.category', 'price_id', string='Règle de Prix', store=True)

    def _tz_get(self):
        return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)
    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get('tz') or self.env.user.tz or 'UTC',
        help="This field is used in order to define in which timezone the resources will work.")

    @api.depends('tz')
    def _compute_tz_offset(self):
        for calendar in self:
            calendar.tz_offset = datetime.now(pytz.timezone(calendar.tz or 'GMT')).strftime('%z')

    @api.constrains('list_price')
    def _constrains_list_price(self):
        hour_per_day = 0
        location_type = self.list_price.filtered(lambda z: z.is_location).mapped('vehicle_location_id')
        for record in self.list_price:
            if record.resource_calendar_id:
                hours = record.resource_calendar_id.hours_per_day
                if not record.is_location:
                    hour_per_day += hours
        if self.list_price:
            message = "24 heures par jour requis pour l'heure de travail du vehicule"
            if hour_per_day and hour_per_day < 24:
                raise ValidationError(message)
            if location_type:
                all_price_location = self.env['price.location'].browse(set(location_type.ids))
                for price in all_price_location:
                    vals = self.list_price.filtered(lambda x: x.is_location and x.vehicle_location_id.id == price.id)
                    values = sum(hour.resource_calendar_id.hours_per_day for hour in vals) if vals else None
                    if values and values < 24:
                        location = f"24 heures par jour requis pour {price.name} du vehicule"
                        raise ValidationError(location)


class FleetVehiclePriceCategory(models.Model):

    _name = "fleet.vehicle.price.category"

    name = fields.Char('Nom')
    price_id = fields.Many2one('fleet.vehicle.model.category', store=True, string="One2many relationnal fields")
    is_location = fields.Boolean(default=False, string="Location")
    applied_on = fields.Selection([
        ('product', 'Article')
    ], default="product", string="Appliqué sur ")
    resource_calendar_id = fields.Many2one('resource.calendar', string="Heures de Travail")
    product_id = fields.Many2one("product.product", string="Article ", required=True)
    product_wait_id = fields.Many2one("product.product", string="application de temps d'attente sur ")
    vehicle_location_id = fields.Many2one('price.location', string='Location')


class LocationPrice(models.Model):

    _name = 'price.location'

    name = fields.Char(string="Nom", required=True)
    price = fields.Monetary(string='Prix', required=True, currency_field='company_currency_id')
    hours = fields.Float(string="durée du location", required=True)
    company_id = fields.Many2one('res.company', store=True, copy=False, default=lambda self: self.env.user.company_id.id)
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
