
from odoo import api, fields, models


class NewsLetterTag(models.Model):
    _name = 'news.letter.tag'

    name = fields.Char(string="Nom")
    color = fields.Integer(string="Couleur")

