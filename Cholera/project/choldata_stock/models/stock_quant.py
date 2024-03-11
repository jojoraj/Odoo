# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_expiry_alert = fields.Boolean(string='Périmé', related='lot_id.product_expiry_alert')