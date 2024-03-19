from odoo import _, models

SEPARATED = ', '


class Invoice(models.Model):
    _inherit = 'account.move'

    def _get_details_line(self):
        """
            :return dict
        """
        move_id = self
        move_line_id = self.invoice_line_ids
        order_ids = move_id.pos_order_ids.lines.mapped('sale_order_origin_id')
        remisage, recuperation = [], []
        for line in order_ids:
            opportunity_id = line.opportunity_id
            if opportunity_id.as_many_course:
                destination = list(set(opportunity_id.others_destination.mapped('name')))
                remisage += destination
            elif opportunity_id.destination_zone:
                remisage.append(opportunity_id.destination_zone)
            elif opportunity_id.destination_zone_id:
                remisage.append(opportunity_id.destination_zone_id.name)
            if opportunity_id.pick_up_zone:
                recuperation.append(opportunity_id.pick_up_zone)
            elif opportunity_id.pick_up_zone_id:
                recuperation.append(opportunity_id.pick_up_zone_id.name)
        role_id = move_id.role_id
        payment_end = ''
        if move_id.invoice_payment_term_id:
            payment_end = move_id.invoice_payment_term_id.name
        elif move_id.invoice_date_due:
            payment_end = move_id.invoice_date_due.strftime('%d/%m/%Y')
        payment_values = {
            'paid': _('Paid'),
            'not_paid': _('Unpaid'),
            'in_payment': _('In payment'),
            'partial': _('Partial payment'),
            'reversed': _('Reversed'),
            'invoicing_legacy': _('Invoicing app legacy'),
        }
        state = {
            'posted': _('posted'),
            'draft': _('draft')
        }
        payment_translate = payment_values.get(move_id.payment_state, '')
        ref_name = [rec.name for rec in order_ids]
        return {
            'partner_invoice': move_id.partner_id.name,
            'invoice_date': move_id.invoice_date.strftime('%d/%m/%Y') if move_id.invoice_date else '-',
            'invoice_e_date': payment_end,
            'price_subtotal': sum(move_line_id.mapped('price_subtotal')),
            'price_total': sum(move_line_id.mapped('price_total')),
            'quantity': sum(x.quantity for x in move_line_id if x.product_uom_id.name in ['km', 'Km']),
            'recuperation': SEPARATED.join(recuperation) if recuperation else '',
            'remisage': SEPARATED.join(remisage) if remisage else '',
            'vehicle_id': role_id.name,
            'ref_bc': SEPARATED.join(ref_name) if ref_name else '',
            'ref_invoice': move_id.name,
            'amount_residual': move_id.amount_residual,
            'amount_untaxed_signed': move_id.amount_untaxed_signed,
            'amount_untaxed': move_id.amount_untaxed,
            'amount_total_signed': move_id.amount_total_signed,
            'payment_state': payment_translate,
            'amount_total': move_id.amount_total,
            'state': state.get(move_id.state, ''),
        }

    def action_consolidate_invoice(self):
        amount_untaxed = sum(self.mapped('amount_untaxed'))
        amount_total = sum(self.mapped('amount_total'))
        amount_residual = sum(self.mapped('amount_residual'))
        currency_id = self.env.company.currency_id
        details = []
        for record in self:
            detail = record._get_details_line()
            details.append(detail)
        amount_text = currency_id.amount_to_text(amount_total)
        moves = self[0] if len(self) > 1 else self
        ref = [x['ref_bc'] for x in details if x.get('ref_bc', False)]
        return {
            'ref_invoices': SEPARATED.join(self.mapped('name')),
            'amount_total': amount_total,
            'amount_tax': sum(self.mapped('amount_tax')),
            'amount_untaxed': amount_untaxed,
            'ref_bc': ', '.join(ref),
            'amount_tex': amount_text,
            'active_ids': self.ids,
            'details': details,
            'docs': moves,
            'account_move': moves,
            'amount_residual': amount_residual
        }
