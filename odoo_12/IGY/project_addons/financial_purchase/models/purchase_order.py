from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    journal_id = fields.Many2one('account.journal', string="Journal")

    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        res.update({
            'context': {
                'type': 'in_invoice',
                'default_purchase_id': self.id,
                'default_currency_id': self.currency_id.id,
                'default_company_id': self.company_id.id,
                'company_id': self.company_id.id,
                'default_origin': self.name,
                'default_reference': self.partner_ref,
                'default_journal_id': self.journal_id.id
            }

        })
        return res

