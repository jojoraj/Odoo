from odoo import api, fields, models, _


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    salary_type = fields.Selection([
        ('gain', _('Gain')),
        ('deduction', _('Deduction')),
        ('intermediate', _('Intermediate'))
    ])
