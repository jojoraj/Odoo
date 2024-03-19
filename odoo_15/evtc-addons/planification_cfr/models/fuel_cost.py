from odoo import api, fields, models
from odoo.addons.fleet.models.fleet_vehicle_model import FUEL_TYPES


class FleetVehicle(models.Model):
    _name = 'fuel.cost'

    name = fields.Selection(FUEL_TYPES, 'Fuel Type', help='Fuel Used by the vehicle', readonly=False)
    # cost = fields.Float(string='Cost')
    product_id = fields.Many2one('product.product', string='Product')
    cost = fields.Monetary(compute='_compute_cost', store=True, readonly=False)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The fuel type must be unique!')
    ]

    @api.depends('product_id')
    def _compute_cost(self):
        for rec in self:
            if rec.product_id:
                rec.cost = rec.product_id.standart_price

    @api.onchange('cost')
    def _onchange_cost(self):
        if self.product_id:
            self.product_id.standart_price = self.cost
