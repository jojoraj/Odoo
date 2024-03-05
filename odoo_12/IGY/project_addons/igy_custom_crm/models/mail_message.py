import threading

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class InheritMailMessage(models.Model):
    """ MassMailing models a wave of emails for a mass mailign campaign.
    A mass mailing is an occurence of sending emails. """

    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        res = super(InheritMailMessage, self).create(values)
        if res.model == "crm.lead":
            current_crm_lead = self.env["crm.lead"].browse(res.res_id)
            if current_crm_lead and current_crm_lead.email_from == res.email_from:
                verification_local_data = self.env['crm.lead.tag'].sudo().search([('name', '=', 'Vérification')], limit=1).mapped('id')
                if len(verification_local_data) > 0:
                    current_crm_lead.write({
                        'tag_ids': [(4, verification_local_data[0])]
                    })
                else:
                    verification_local_data = self.env['crm.lead.tag'].sudo().create({
                        'name': 'Vérification'
                    })
                    current_crm_lead.write({
                        'tag_ids': [(4, verification_local_data.id)]
                    })

        return res

