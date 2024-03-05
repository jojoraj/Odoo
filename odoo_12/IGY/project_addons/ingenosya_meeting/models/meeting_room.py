# -*- coding: utf-8 -*-

from odoo import fields ,models ,api

class Room(models.Model):
    _name = 'meeting.room'

    name = fields.Char(string="Nom", copy=False)
    description = fields.Text(string="Description")
    maximum_available = fields.Integer(string="Nombre de personne maximum")
