# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class TrackingPriceMinimum(models.Model):
    _name = 'fleet.vehicle.model.category'
    _inherit = ['fleet.vehicle.model.category', 'mail.thread', 'mail.activity.mixin']

    minimum_price_id = fields.Many2one('account.minimum.price', tracking=True)