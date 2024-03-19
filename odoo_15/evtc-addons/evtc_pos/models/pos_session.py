from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super(PosSession, self)._validate_session(balancing_account, amount_to_balance, bank_payment_method_diffs)
        orders = self.order_ids.filtered(lambda o: o.state in ['done', 'invoiced'])
        for order in orders:
            for so in order.lines.mapped('sale_order_origin_id'):
                if self.env.ref('esanandro_crm.stage_lead6').id == so.opportunity_id.stage_id.id:
                    so.opportunity_id.stage_id = self.env.ref('crm.stage_lead4').id
        return res
