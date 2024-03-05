import threading

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class MassMailing(models.Model):
    """ MassMailing models a wave of emails for a mass mailign campaign.
    A mass mailing is an occurence of sending emails. """

    _inherit = 'mail.mass_mailing'

    sent_by_minute = fields.Integer(string="Mail sent by minute", default=5)

    #selet radio button type of mail
    mail_type = fields.Selection([('cold', 'Cold Mailing.'), ('cv', 'Envoi CV'), ('none', 'Aucun')], string='Type', required=True)
    total_mail_sent = fields.Integer(string="Total mail sent", help="This field compute the sent mail to prevent "
                                                                    "from reaching limit", default=0)
    limit = fields.Integer(string="Limite", default=200)

    date_now = fields.Datetime(String="Date d'envoi")

    def send_mail(self, res_ids=None):
        author_id = self.env.user.partner_id.id

        for mailing in self:
            if mailing.reply_to_mode == 'email' and mailing.mail_type == 'cv':
                mailing.sudo().write({
                    'keep_archives': True
                })
            if not res_ids:
                res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There is no recipients selected.'))

            #get list of self.sent_by_minute first item in res_ids
            res_ids = res_ids[:self.sent_by_minute]

            composer_values = {
                'author_id': author_id,
                'attachment_ids': [(4, attachment.id) for attachment in mailing.attachment_ids],
                'body': mailing.body_html,
                'subject': mailing.name,
                'model': mailing.mailing_model_real,
                'email_from': mailing.email_from,
                'record_name': False,
                'composition_mode': 'mass_mail',
                'mass_mailing_id': mailing.id,
                'mailing_list_ids': [(4, l.id) for l in mailing.contact_list_ids],
                'no_auto_thread': mailing.reply_to_mode != 'thread',
                'template_id': None,
                'mail_server_id': mailing.mail_server_id.id,
                'crm_lead_ids': [(6, 0, res_ids)],
                'mail_type': mailing.mail_type,
            }
            if mailing.reply_to_mode == 'email':
                composer_values['reply_to'] = mailing.reply_to
                composer_values['no_auto_thread'] = False

            composer = self.env['mail.compose.message'].with_context(active_ids=res_ids).create(composer_values)
            extra_context = self._get_mass_mailing_context()
            composer = composer.with_context(active_ids=res_ids, **extra_context)
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            composer.send_mail(auto_commit=auto_commit)

            # We get count the number of sent mail
            mailing.total_mail_sent += len(res_ids) if len(res_ids) <= self.sent_by_minute else self.sent_by_minute
            if mailing.total_mail_sent >= mailing.limit:
                mailing.write({'state': 'done'})

            # change stage_id of crm.lead
            if mailing.mailing_model_real == 'crm.lead':
                for lead in self.env['crm.lead'].sudo().browse(res_ids):
                    if mailing.mail_type == 'cold':
                        lead = lead.with_context(from_mailing=True)
                        if lead.stage_id.id == self.env.ref('igy_custom_crm.igy_qualification_marketting').id:
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_first_send').id
                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_first_send').id:
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_second_send').id
                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_second_send').id:
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_third_send').id
                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_third_send').id:
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_fourth_send').id

                    # Update the lead original mailing
                    lead.last_mass_mailing_id = self.id
        return True

    @api.model
    def create(self, vals):
        """Override the create method to set the total mail sent to 0 when we duplicate mass_mailing"""
        res = super(MassMailing, self).create(vals)
        if res.total_mail_sent != 0:
            res.total_mail_sent = 0
        return res

    @api.multi
    def put_in_queue(self):
        self.date_now = fields.datetime.now()
        return super(MassMailing, self).put_in_queue()
