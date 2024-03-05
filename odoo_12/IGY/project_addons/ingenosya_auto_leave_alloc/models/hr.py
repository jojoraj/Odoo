# -*- coding: UTF-8 -*-

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    allocation = fields.Float(string="Allocation in day(s)", default=0.00, copy=False, digits=dp.get_precision('Allocation precision'))
