# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BoxMaterial(models.Model):
    _name = 'box.material'

    name = fields.Char(string=_("Nom du box internet"), required=True)
    description = fields.Text(string=_("Description"))