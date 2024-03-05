from datetime import date, datetime, timedelta

from odoo import models, fields, api, _

from odoo.exceptions import UserError

import threading


class MailMassMailingCold(models.Model):
    _name = 'mail.mass_mailing_cold'
    _order = "name"
    _inherit = "mail.mass_mailing"
    _description = "mass mailing cold inherit"

    description = fields.Char(String='Déscription')

    custom_date = fields.Integer(string='Date de prochaine envoi (Jours)', track_visibility='onchange')

    contact_list_ids = fields.Many2many('mail.mass_mailing.list', 'mail_mass_mailing_list_rel_cold',
                                        string='Mailing Lists')

    def send_mail(self, res_ids=None):
        author_id = self.env.user.partner_id.id
        for mailing in self:
            if not res_ids:
                res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There is no recipients selected.'))

            # get list of self.sent_by_minute first item in res_ids
            if mailing.id == self.env.ref('igy_custom_crm.record_mass_mailing_cold').id:
                pass
            else:
                res_ids = self.env['crm.lead'].browse(res_ids).filtered(lambda x: x.date_store == fields.date.today()).mapped('id')

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
                'mass_mailing_cold_id': mailing.id,
                'mailing_list_ids': [(4, l.id) for l in mailing.contact_list_ids],
                'no_auto_thread': mailing.reply_to_mode != 'thread',
                'template_id': None,
                'mail_server_id': mailing.mail_server_id.id,
                'crm_lead_ids': [(6, 0, res_ids)] if self.mailing_model_name == 'crm.lead' else None,
                'mail_type': mailing.mail_type,
            }
            if mailing.reply_to_mode == 'email':
                composer_values['reply_to'] = mailing.reply_to

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
                        if lead.stage_id.id == self.env.ref('igy_custom_crm.igy_qualification_marketting').id:
                            mailing_qualif = self.env['ir.config_parameter'].sudo().get_param('mass_mailing.interval_day_first_sent')
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_first_send').id
                            lead.write({
                                'date_store': fields.date.today() + timedelta(days=int(mailing_qualif))
                            })

                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_first_send').id:
                            mailing_1st = self.env['ir.config_parameter'].sudo().get_param('mass_mailing.interval_day_second_sent')
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_second_send').id
                            lead.write({
                                'date_store': fields.date.today() + timedelta(days=int(mailing_1st))
                            })

                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_second_send').id:
                            mailing_2nd = self.env['ir.config_parameter'].sudo().get_param('mass_mailing.interval_day_third_sent')
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_third_send').id
                            lead.write({
                                'date_store': fields.date.today() + timedelta(days=int(mailing_2nd))
                            })
                        elif lead.stage_id.id == self.env.ref('igy_custom_crm.igy_third_send').id:
                            lead.stage_id = self.env.ref('igy_custom_crm.igy_fourth_send').id

                    # Update the lead original mailing
                    lead.crm_lead_cold_id = self.id
        return True

    @api.model
    def action_date(self):
        mass_mailings = self.search(
            [('state', 'in', ('in_queue', 'sending')), '|', ('schedule_date', '<', fields.Datetime.now()),
             ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            user = mass_mailing.write_uid or self.env.user
            mass_mailing = mass_mailing.with_context(**user.sudo(user=user).context_get())
            if len(mass_mailing.get_remaining_recipients()) > 0:
                mass_mailing.state = 'sending'
                mass_mailing.send_mail()
            else:
                mass_mailing.write({'state': 'in_queue', 'sent_date': fields.Datetime.now()})
