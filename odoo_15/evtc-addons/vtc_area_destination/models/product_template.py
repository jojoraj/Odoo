from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    time_wait_ok = fields.Boolean(string="Est un temps d'attente")
