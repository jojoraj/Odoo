# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    is_medicament = fields.Boolean(related="product_id.is_medicament")
