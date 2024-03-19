from odoo import fields, models


class TariffPlan(models.Model):
    _name = 'esanandro_geotab.tariff.plan'
    _description = 'Tariff plan'

    name = fields.Char(string='name')
    product_template_id = fields.Many2one(comodel_name='product.product', string='Product')
    list_price = fields.Float(related='product_template_id.list_price', readonly=True)
    fleet_vehicle_ids = fields.Many2many(comodel_name='fleet.vehicle', string='Vehicle')
