# -*- coding: UTF-8 -*-

from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_current_year_type = fields.Boolean(string="Is current year auto. allocation", default=False, copy=False)
