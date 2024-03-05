# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeLines(models.Model):
    _name = "hr.employee.lines"

    child_id = fields.Many2one('hr.employee', string="Children ID")
    child_name = fields.Char(string="Name")
    child_gender = fields.Selection([
        ('masculin', 'Masculin'),
        ('feminin', 'Feminin')
    ], string="Gender", default="masculin")
    child_birthday = fields.Date(string="Date of birth")
    place_birthday = fields.Char(string="Place of birth")