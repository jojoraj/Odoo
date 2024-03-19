from odoo import _, fields, models


class AccountMoveSeq(models.Model):
    _inherit = 'account.move'

    sequence_activated = fields.Boolean(default=False)

    def write(self, vals):
        super(AccountMoveSeq, self).write(vals)
        if not self.sequence_activated and self.state == 'posted':
            self.sequence_activated = True
            if self and self.partner_id:
                if self.partner_id.company_type == 'person':
                    self.name = self.env['ir.sequence'].next_by_code('account.move.particularity.sequence') or _(
                        'draft')
                else:
                    self.name = self.env['ir.sequence'].next_by_code('account.move.society.sequence') or _('draft')
