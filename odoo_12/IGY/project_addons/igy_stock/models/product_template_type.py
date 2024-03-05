from odoo import api, fields, models


class ProductTemplateType(models.Model):
    _name = 'product.template.type'

    name = fields.Char(string="Name")
