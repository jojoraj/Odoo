from odoo import api, fields, models


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    is_irsa_child_decuction = fields.Boolean(string="Deduction nombre d'enfant", default=False)
    child_number = fields.Integer(string="Nombre d'enfant")

    @api.onchange('is_irsa_child_decuction', 'child_number')
    def set_amount(self):
        for rec in self:
            if rec.is_irsa_child_decuction:
                rec.name = 'Deduction IRSA'
                rec.code = 'DED_CHILD'
            if rec.is_irsa_child_decuction and rec.child_number > 0:
                rec.amount = 2000 * rec.child_number


