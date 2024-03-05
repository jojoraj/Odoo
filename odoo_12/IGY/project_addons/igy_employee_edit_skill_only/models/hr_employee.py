# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_RH = fields.Boolean(compute="_compute_is_RH",default=lambda self: True if self.env.user.has_group('hr.group_hr_manager') else False)

    def _compute_is_RH(self):
        if self.env.user.has_group('hr.group_hr_manager'):
            self.is_RH = True
        else:
            self.is_RH = False