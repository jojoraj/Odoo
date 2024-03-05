# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    public_holiday_id = fields.Many2one("public.holiday", string='Jour férié')
    active = fields.Boolean(string="Active", default=True)

