import logging
import re
from ast import literal_eval

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

TYPES_VALUE = {
    '3': _('canceled'),
    '2': _('validate')
}


class MailContent(models.Model):
    _name = 'evtc.mail.content'
    _description = 'define type of mail'

    name = fields.Char(compute='_compute_name')
    types = fields.Selection([
        ('1', _(U'Create')),
        ('2', _('Validate')),
        ('3', _('Canceled'))
    ])
    help = fields.Char(default=""" <h3> Add dynamique body field </h3> : <br/> <small> ex: {record.partner_id.name} =>
                       for partner name. record is the instance of crm_lead </small>.<br/> All attributes of crm lead object can be passed from record.""",
                       readonly=True)
    header = fields.Char('Message Header', required=True)
    body = fields.Html('Message Body', required=True)
    active = fields.Boolean(default=True)

    @api.onchange('types')
    def _compute_name(self):
        self.name = _('Notification for %s') % (TYPES_VALUE.get(self.types, _('create')))


class ReservationNotification(models.Model):
    _inherit = 'crm.lead'
    _description = 'send mail after crm created'

    @api.model
    def get_content_mail_header(self, types, current_id):
        notif_content = self.env['evtc.mail.content'].search([
            ('types', 'ilike', types),
            ('active', '=', True)
        ], order='create_date desc', limit=1)
        if notif_content:
            header = notif_content.header
            evaluate_header = re.findall(r'(?:{[a-z]+).[a-z]+.[a-z]+.\w+}', header)
            for j in evaluate_header:
                head = j.strip()[1:-1]
                header = header.replace(j, str(literal_eval(head)))
            string = notif_content.body
            evaluate = re.findall(r'(?:{[a-z]+).[a-z]+.[a-z]+.\w+}', string)
            for rec in evaluate:
                strip_string = rec.strip()[1:-1]
                string = string.replace(rec, str(literal_eval(strip_string)))
            return header, string
        return None, None

    @api.model
    def create(self, value):
        """
        send mail for notification value
        parms: value
        """
        crm_lead = super(ReservationNotification, self).create(value)
        partner_id = crm_lead.partner_id
        country_id = partner_id.country_id
        crm_lead.reference_code = f'L{crm_lead.id}'
        if country_id and country_id.code == 'MG':
            user_id = partner_id.user_ids[0] if partner_id.user_ids else self.env['res.users']
            sms_id = self.env.ref('esanandro_crm.sms_template_data_crm_lead_create_notification')
            string = sms_id._render_field('body', [crm_lead.id], set_lang=sms_id.lang)[crm_lead.id]
            user_id.send_orange_sms(body=string, force_send=True, senders=partner_id)
        else:
            crm_id = crm_lead.id
            if partner_id.email or partner_id.user_id.login:
                try:
                    mail_template = self.env.ref('esanandro_crm.email_template_data_crm_lead_create_notification',
                                                 raise_if_not_found=False)
                    try:
                        mail_template.send_mail(crm_id, force_send=True)
                        msg = "{} e-mail has been successfully send with {} on crm created {}"
                        _logger.info(msg.format('=' * 25, partner_id.email or partner_id.user_id.login, '=' * 25))
                    except Exception as e:
                        _logger.error(e)
                except ValueError as e:
                    _logger.error("{} the mail template has not been created : {} {}".format('=' * 25, e, '=' * 25))
        return crm_lead

    def write(self, values):
        """
            mail notification
            reservation canceled
            params: values
        """
        vals = super(ReservationNotification, self).write(values)
        if vals:
            try:
                template_mail = self.env.ref('esanandro_crm.email_template_data_crm_lead_refused_notification',
                                             raise_if_not_found=False)
                
                if values.get('stage_id', False) and self.env.ref('esanandro_crm.stage_lead5').id == values.get(
                        'stage_id'):
                    if self.refusal_ids and self.refusal_remark:
                        if self.partner_id.country_id.code == 'MG':
                            partner_id = self.partner_id
                            user_id = partner_id.user_ids[0] if partner_id and partner_id.user_ids else self.env['res.users']
                            sms_id = self.env.ref('esanandro_crm.sms_template_data_crm_lead_refused_notification')
                            string = sms_id._render_field('body', [self.id], set_lang=sms_id.lang)[self.id]
                            user_id.send_orange_sms(body=string, force_send=True, senders=partner_id)
                        else:
                            try:
                                template_mail.send_mail(self.id, force_send=True)
                            except Exception as e:
                                _logger.info(f"{'=' * 25} Mail has been not send with reason: {str(e)} {'=' * 25}")
            except ValueError as e:
                _logger.info("{} the mail template has not been created : {} {} ".format('=' * 25, e, '=' * 25))
        return vals
