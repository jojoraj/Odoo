from odoo import models, fields

class StockManagment(models.Model):
    _name = "stock.managment"

    product = fields.Char(string="Produit")
