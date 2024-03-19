import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AutoPlanningNotification(models.TransientModel):
    _inherit = 'auto.planning.wizard'
    _description = 'Sending notification while reservation will be affected'

    def validate(self):
        record_id = self.env['crm.lead'].sudo().browse(self._context.get('active_ids'))
        validate = super(AutoPlanningNotification, self).validate()
        try:
            if self.env.ref('crm.stage_lead2').id == record_id.stage_id.id:
                partner_id = record_id.partner_id
                country_id = partner_id.country_id
                user_id = record_id.partner_id.user_ids[0] if record_id.partner_id.user_ids else self.env['res.users']
                if country_id and country_id.code == 'MG':
                    user_id = partner_id.user_ids[0] if partner_id.user_ids else self.env['res.users']
                    sms_id = self.env.ref('esanandro_crm.sms_template_data_crm_lead_validate_notification')
                    string = sms_id._render_field('body', [record_id.id], set_lang=sms_id.lang)[record_id.id]
                    user_id.send_orange_sms(body=string, force_send=True, senders=partner_id)
                else:
                    try:
                        template_mail_lead7 = self.env.ref(
                            'esanandro_crm.email_crm_affected',
                            raise_if_not_found=False)
                        template_mail_lead7.send_mail(record_id.id, force_send=True)
                    except Exception as e:
                        _logger.info(f"{'=' * 25} Mail has been not send with reason: {str(e)} {'=' * 25}")
        except ValueError as e:
            _logger.error(f"the mail template has not been created {str(e)} ")
        return validate
