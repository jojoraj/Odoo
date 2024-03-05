from odoo import api, fields, models, _


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    salary_type = fields.Selection([
        ('gain', _('Gain')),
        ('deduction', _('deduction')),
        ('intermediate', _('Intermediate'))
    ], related='salary_rule_id.salary_type', store=True)
