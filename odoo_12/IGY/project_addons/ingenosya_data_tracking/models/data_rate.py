# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Rate(models.Model):
    _name = "data.tracking.rate"

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    name = fields.Char(string="Name", copy=False)
    data = fields.Float(string="Data (mo)", copy=False)
    data_validity = fields.Integer(string="Validity (days)", copy=False)
    amount = fields.Float(string="Price", copy=False)
    type_validity = fields.Selection([('Cumulative', 'Cumulative'), ('New', 'New')], copy=False)
    employee_id = fields.Many2one('res.users', default=lambda self: self.env.uid)
