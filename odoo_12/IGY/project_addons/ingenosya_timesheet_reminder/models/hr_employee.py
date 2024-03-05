from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    date_begin_work = fields.Date(string="Première date de travail")

    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        for line in self:
            if 'active' in vals.keys():
                analytic_lines = self.env['account.analytic.line'].search([
                    ('employee_id', '=', line.id),
                    ('public_holiday_id', '!=', False)
                ])
                analytic_lines.sudo().write({
                    'active': vals.get('active')
                })
        return res
