
from odoo import api, fields, models


class FaqModels(models.Model):
    _name = 'faq.models'

    name = fields.Char(string="Nom")
