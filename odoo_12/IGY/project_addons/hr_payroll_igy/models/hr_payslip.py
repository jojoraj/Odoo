from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    amount_to_pay = fields.Float(string="Amount to pay", compute='_compute_amount_to_pay', store=True)
    total_gain = fields.Float(string="Total gain", compute='_compute_total_gain', store=True)
    total_deduction = fields.Float(string="Total gain", compute='_compute_total_deduction', store=True)
    currency_id = fields.Many2one('res.currency', string="Devise", default=lambda self: self.env.user.company_id.currency_id.id)

    @api.depends('line_ids')
    def _compute_total_gain(self):
        for rec in self:
            if len(rec.line_ids) > 0:
                gains = rec.line_ids.filtered(lambda x: x.category_id.code == 'TOTAL_GAIN')
                if gains:
                    rec.total_gain = gains.total
                else:
                    rec.total_gain = 0
            else:
                rec.total_gain = 0

    @api.depends('line_ids')
    def _compute_total_deduction(self):
        for rec in self:
            if len(rec.line_ids) > 0:
                deductions = rec.line_ids.filtered(lambda x: x.category_id.code == 'TOTAL_RETENU')
                if deductions:
                    rec.total_deduction = deductions.total
                else:
                    rec.total_deduction = 0
            else:
                rec.total_deduction = 0

    @api.depends('total_gain', 'total_deduction')
    def _compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.total_gain - rec.total_deduction

    @api.multi
    def action_payslip_cancel(self):
        # if self.filtered(lambda slip: slip.state == 'done'):
        #     raise UserError(_("Cannot cancel a payslip that is done."))
        return self.write({'state': 'cancel'})
