# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SanitaryTraining(models.Model):
    _name = 'sanitary.training'

    name = fields.Char(string='Formation sanitaire')
