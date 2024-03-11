# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SanitaryTraining(models.Model):
    _name = 'water.source'

    name = fields.Char(string='Source de consommation')
