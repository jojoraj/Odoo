from odoo import api, fields, models


class ProductHistoryType(models.Model):
    _name = 'product.history.type'

    name = fields.Char(string="Nom")
    type = fields.Selection([
        ('attribution', 'Attribution'),
        ('restitution', 'Restitution'),
        ('broken', 'En panne'),
        ('return_repair', 'Retour de réparation')
    ])
