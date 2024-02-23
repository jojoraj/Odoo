from odoo import models, fields, api, _


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    @api.onchange('mailing_model_id', 'contact_list_ids')
    def _onchange_model_and_list(self):
        if self.mailing_model_name == 'crm.lead':
            return
        mailing_domain = []
        if self.mailing_model_name:
            if self.mailing_model_name == 'mail.mass_mailing.list':
                if self.contact_list_ids:
                    mailing_domain.append(('list_ids', 'in', self.contact_list_ids.ids))
                else:
                    mailing_domain.append((0, '=', 1))
            elif self.mailing_model_name == 'res.partner':
                mailing_domain.append(('customer', '=', True))
            elif 'opt_out' in self.env[self.mailing_model_name]._fields and not self.mailing_domain:
                mailing_domain.append(('opt_out', '=', False))
        else:
            mailing_domain.append((0, '=', 1))
        self.mailing_domain = repr(mailing_domain)
        self.body_html = "on_change_model_and_list"
