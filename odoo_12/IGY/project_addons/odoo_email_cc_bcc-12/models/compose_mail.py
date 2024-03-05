# -*- coding: utf-8 -*-
##############################################################################
#
#  Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##############################################################################

import base64
import datetime
import logging
import psycopg2
import threading
import re
from pytz import timezone
from email.utils import formataddr
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    display_cc_recipients = fields.Boolean(
        string="Display Recipients Cc (Partners)", default=True)
    display_bcc_recipients = fields.Boolean(
        string="Display Recipients Bcc (Partners)", default=True)
    display_cc = fields.Boolean(string="Display Cc (Emails)")
    display_bcc = fields.Boolean(string="Display Bcc (Emails)")
    display_reply_to = fields.Boolean(string="Display Reply To")
    default_cc = fields.Char(
        'Default Cc (Emails)', help='Carbon copy message recipients (Emails)')
    default_bcc = fields.Char(
        'Default Bcc (Emails)',
        help='Blind carbon copy message recipients (Emails)')
    default_reply_to = fields.Char('Default Reply To')


class MailComposer(models.TransientModel):
    """ Generic message composition wizard. You may inherit from this wizard
        at model and view levels to provide specific features.

        The behavior of the wizard depends on the composition_mode field:
        - 'comment': post on a record. The wizard is pre-populated via \
        ``get_record_data``
        - 'mass_mail': wizard in mass mailing mode where the mail details can
            contain template placeholders that will be merged with actual data
            before being sent to each recipient.
    """
    _inherit = 'mail.compose.message'

    @api.model
    def get_default_cc_email(self):
        if self.env.user.company_id.display_cc:
            return self.env.user.company_id.default_cc
        return False

    @api.model
    def get_default_bcc_emails(self):
        if self.env.user.company_id.display_bcc:
            return self.env.user.company_id.default_bcc
        return False

    @api.model
    def get_default_reply_to(self):
        if self.env.user.company_id.display_reply_to:
            return self.env.user.company_id.default_reply_to
        return False

    email_bcc = fields.Char(
        'Bcc (Emails)', help='Blind carbon copy message (Emails)',
        default=get_default_bcc_emails)
    email_cc = fields.Char(
        'Cc (Emails)', help='Carbon copy message recipients (Emails)',
        default=get_default_cc_email)
    cc_recipient_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_cc_rel',
        'wizard_id', 'partner_id', string='Cc (Partners)')
    bcc_recipient_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_bcc_rel',
        'wizard_id', 'partner_id', string='Bcc (Partners)')
    display_cc = fields.Boolean(
        string="Display Cc",
        default=lambda self: self.env.user.company_id.display_cc, )
    display_bcc = fields.Boolean(
        string="Display Bcc",
        default=lambda self: self.env.user.company_id.display_bcc, )
    display_cc_recipients = fields.Boolean(
        string="Display Recipients Cc (Partners)",
        default=lambda self: self.env.user.company_id.display_cc_recipients, )
    display_bcc_recipients = fields.Boolean(
        string="Display Recipients Cc (Partners)",
        default=lambda self: self.env.user.company_id.display_bcc_recipients)
    display_reply_to = fields.Boolean(
        string="Display Reply To",
        default=lambda self: self.env.user.company_id.display_reply_to, )
    email_to = fields.Text('To', help='Message recipients (emails)')
    reply_to = fields.Char(
        'Reply-To',
        help='Reply email address. Setting the reply_to bypasses the \
        automatic thread creation.', default=get_default_reply_to)

    @api.multi
    def get_mail_values(self, res_ids):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        self.ensure_one()
        results = super(MailComposer, self).get_mail_values(res_ids)
        for res_id in res_ids:
            # static wizard (mail.message) values
            results[res_id].update({
                'email_bcc': self.email_bcc,
                'email_cc': self.email_cc,
                'cc_recipient_ids': self.cc_recipient_ids,
                'bcc_recipient_ids': self.bcc_recipient_ids,
                'reply_to': self.reply_to,
                # 'email_to': self.email_to,
            })
        if self.email_to:
            results['to'] = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
                'email_bcc': self.email_bcc,
                'email_cc': self.email_cc,
                'cc_recipient_ids': self.cc_recipient_ids,
                'bcc_recipient_ids': self.bcc_recipient_ids,
                'reply_to': self.reply_to,
                'email_to': self.email_to,
                'body_html': self.body or ''
            }
        elif not self.email_to and (self.email_cc or self.cc_recipient_ids):
            results['cc'] = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
                'email_bcc': self.email_bcc,
                'email_cc': self.email_cc,
                'cc_recipient_ids': self.cc_recipient_ids,
                'bcc_recipient_ids': self.bcc_recipient_ids,
                'reply_to': self.reply_to,
                'email_to': self.email_to,
                'body_html': self.body or ''
            }
        return results

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        notif_layout = self._context.get('custom_layout')
        # Several custom layouts make use of the model description at rendering, e.g. in the
        # 'View <document>' button. Some models are used for different business concepts, such as
        # 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
        # different wording depending on the state of the object.
        # Therefore, we can set the description in the context from the beginning to avoid falling
        # back on the regular display_name retrieved in '_notify_prepare_template_context'.
        model_description = self._context.get('model_description')
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(
                            attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model] if wizard.model and hasattr(self.env[wizard.model],
                                                                             'message_post') else self.env[
                'mail.thread']
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (
                    wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            #features IGY START
            alterning_mail_server_env = self.env['alterning.mail.server']
            alterning_mail_server_line_env = self.env['alterning.mail.server.line']
            alterning_mail_server_record = self.env.ref(
                'igy_alterning_mail_server.alterning_mail_server_record')

            alterning_mail_server_line_ids = alterning_mail_server_line_env.sudo().search(
                [('alterning_id', '=', alterning_mail_server_record.id),
                 ('is_current_server', '=', True)], limit=1)

            for alterning_mail_server_line_id in alterning_mail_server_line_ids:
                date_now = datetime.datetime.strptime(datetime.datetime.now().astimezone(
                    timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S.%fz"),
                                                      "%Y-%m-%dT%H:%M:%S.%fz")
                hour_difference = ((
                                           date_now - alterning_mail_server_line_id.create_date).total_seconds()) / 3600
                if int(hour_difference) >= 1 and alterning_mail_server_record.in_use:
                    alterning_mail_server_env.execute_alterning_mail_server()
            # features IGY END

            for res_ids in sliced_res_ids:
                batch_mails = Mail
                all_mail_values = wizard.get_mail_values(res_ids)
                count_mail = 0
                for res_id, mail_values in all_mail_values.items():
                    # features IGY START
                    try:
                        if alterning_mail_server_record.in_use:
                            mail_server_line_ids = alterning_mail_server_line_env.sudo().search(
                                [('alterning_id', '=', alterning_mail_server_record.id),
                                 ('is_current_server', '=', True)]).mapped('name.id')
                            if alterning_mail_server_record.autorize_server_choice:
                                if mail_values.get('mail_server_id', False) == False:
                                    mail_values['mail_server_id'] = mail_server_line_ids[count_mail]
                            else:
                                mail_values['mail_server_id'] = mail_server_line_ids[count_mail]

                            self.env['ir.mail.log'].sudo().create({
                                'name': mail_values.get('mail_server_id', False),
                                'email_to': mail_values['email_to'],
                                'date': fields.Date.today()
                            })

                        count_mail += 1
                        if count_mail == len(alterning_mail_server_record.alterning_line_ids.filtered(
                                lambda x: x.is_current_server == True).mapped('id')):
                            count_mail = 0

                    except:
                        pass
                    # features IGY END

                    if wizard.composition_mode == 'mass_mail':
                        batch_mails |= Mail.create(mail_values)
                    else:
                        post_params = dict(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            notif_layout=notif_layout,
                            add_sign=not bool(wizard.template_id),
                            mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else False,
                            model_description=model_description,
                            **mail_values)
                        if ActiveModel._name == 'mail.thread' and wizard.model:
                            post_params['model'] = wizard.model
                        if res_id not in ['to', 'cc']:
                            ActiveModel.browse(res_id).message_post(**post_params)
                        else:
                            to_mail = Mail.create(mail_values)
                            if mail_values.get('cc_recipient_ids'):
                                to_mail.cc_recipient_ids = [(6, 0, mail_values.get('cc_recipient_ids').ids)]
                                to_mail.res_id = False
                                to_mail.model = False
                            to_mail.send(auto_commit=auto_commit)

                if wizard.composition_mode == 'mass_mail':
                    batch_mails.send(auto_commit=auto_commit)


class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    email_bcc = fields.Char(
        'Bcc (Emails)',
        help='Blind carbon copy message (Emails)')
    email_cc = fields.Char(
        'Cc (Emails)', help='Carbon copy message recipients (Emails)')
    cc_recipient_ids = fields.Many2many(
        'res.partner', 'mail_message_res_partner_cc_rel',
        'message_id', 'partner_id', string='Cc (Partners)')
    bcc_recipient_ids = fields.Many2many(
        'res.partner', 'mail_message_res_partner_bcc_rel',
        'message_id', 'partner_id', string='Bcc (Partners)')
    email_to = fields.Text('To', help='Message recipients (emails)')


class Mail(models.Model):
    _inherit = "mail.mail"

    @api.multi
    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        IrMailServer = self.env['ir.mail_server']
        IrAttachment = self.env['ir.attachment']
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != 'outgoing':
                    if mail.state != 'exception' and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # remove attachments if user send the link with the access_token
                body = mail.body_html or ''
                attachments = mail.attachment_ids
                for link in re.findall(r'/web/(?:content|image)/([0-9]+)', body):
                    attachments = attachments - IrAttachment.browse(int(link))

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [(a['datas_fname'], base64.b64decode(a['datas']), a['mimetype'])
                               for a in attachments.sudo().read(['datas_fname', 'datas', 'mimetype'])]

                # specific behavior to customize the send email for notified partners
                email_list = []
                cc_list = []
                bcc_list = []
                if mail.email_to:
                    email_list.append(mail._send_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_prepare_values(partner=partner)
                    values['partner_id'] = partner
                    email_list.append(values)
                for partner in mail.cc_recipient_ids:
                    cc_list += mail._send_prepare_values(
                        partner=partner).get('email_to')
                for partner in mail.bcc_recipient_ids:
                    bcc_list += mail._send_prepare_values(
                        partner=partner).get('email_to')

                # headers
                headers = {}
                ICP = self.env['ir.config_parameter'].sudo()
                bounce_alias = ICP.get_param("mail.bounce.alias")
                catchall_domain = ICP.get_param("mail.catchall.domain")
                if bounce_alias and catchall_domain:
                    if mail.model and mail.res_id:
                        headers['Return-Path'] = '%s+%d-%s-%d@%s' % (
                            bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s+%d@%s' % (bounce_alias, mail.id, catchall_domain)
                if mail.headers:
                    try:
                        headers.update(safe_eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _(
                        'Error without exception. Probably due do sending an email without computed recipients.'),
                })
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env['mail.notification'].search([
                    ('is_email', '=', True),
                    ('mail_id', 'in', mail.ids),
                    ('email_status', 'not in', ('sent', 'canceled'))
                ])
                if notifs:
                    notif_msg = _(
                        'Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator.')
                    notifs.write({
                        'email_status': 'exception',
                        'failure_type': 'UNKNOWN',
                        'failure_reason': notif_msg,
                    })

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    if email.get('email_to'):
                        msg = IrMailServer.build_email(
                            email_from=mail.email_from,
                            email_to=email.get('email_to'),
                            subject=mail.subject,
                            body=email.get('body'),
                            body_alternative=email.get('body_alternative'),
                            email_cc=tools.email_split(mail.email_cc) + cc_list,
                            email_bcc=tools.email_split(mail.email_bcc) + bcc_list,
                            reply_to=mail.reply_to,
                            attachments=attachments,
                            message_id=mail.message_id,
                            references=mail.references,
                            object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                            subtype='html',
                            subtype_alternative='plain',
                            headers=headers)
                        processing_pid = email.pop("partner_id", None)
                        try:
                            res = IrMailServer.send_email(
                                msg, mail_server_id=mail.mail_server_id.id, smtp_session=smtp_session)

                            print('Test debug (server id) : ', mail.mail_server_id.id)
                            if processing_pid:
                                success_pids.append(processing_pid)
                            processing_pid = None
                        except AssertionError as error:
                            if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                                failure_type = "RECIPIENT"
                                # No valid recipient found for this particular
                                # mail item -> ignore error to avoid blocking
                                # delivery to next recipients, if any. If this is
                                # the only recipient, the mail will show as failed.
                                _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                             mail.message_id, email.get('email_to'))
                            else:
                                raise
                if res:  # mail has been sent at least once, no major exception occured
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                    # /!\ can't use mail.state here, as mail.refresh() will cause an error
                    # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(success_pids=success_pids, failure_type=failure_type)
            except UnicodeEncodeError as exc:
                _logger.exception('UnicodeEncodeError on text "%s" while processing mail ID %r.', exc.object, mail.id)
                raise MailDeliveryException(_("Mail Delivery Failed"), "Invalid text: %s" % exc.object)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except psycopg2.Error:
                # If an error with the database occurs, chances are that the cursor is unusable.
                # This will lead to an `psycopg2.InternalError` being raised when trying to write
                # `state`, shadowing the original exception and forbid a retry on concurrent
                # update. Let's bubble it.
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({'state': 'exception', 'failure_reason': failure_reason})
                mail._postprocess_sent_message(success_pids=success_pids, failure_reason=failure_reason,
                                               failure_type='UNKNOWN')
                if raise_exception:
                    if isinstance(e, AssertionError):
                        # get the args of the original error, wrap into a value and throw a MailDeliveryException
                        # that is an except_orm, with name and value as arguments
                        value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True


class Thread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.multi
    def _notify_specific_email_values(self, message):
        res = super(Thread, self)._notify_specific_email_values(message)
        if message:
            res.update({
                'email_bcc': message.email_bcc,
                'email_cc': message.email_cc,
                'email_to': message.email_to,
                'cc_recipient_ids': message.cc_recipient_ids,
                'bcc_recipient_ids': message.bcc_recipient_ids,
            })
        return res

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body='', subject=None,
                     message_type='notification', subtype=None,
                     parent_id=False, attachments=None,
                     notif_layout=False, add_sign=False, model_description=False,
                     mail_auto_delete=True, **kwargs):
        """ Post a new message in an existing thread, returning the new
            mail.message ID.
            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.type field
            :param int parent_id: handle reply to a previous message by adding the
                parent partners to the message in case of private discussion
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded
            Extra keyword arguments will be used as default column values for the
            new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document; attach them
                    to the related document. Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        if attachments is None:
            attachments = {}
        if self.ids and not self.ensure_one():
            raise exceptions.Warning(
                _('Invalid record set: should be called as model (without records) or on single-record recordset'))

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context.
        model = False
        if self.ids:
            self.ensure_one()
            model = kwargs.get('model', False) if self._name == 'mail.thread' else self._name
            if model and model != self._name and hasattr(self.env[model], 'message_post'):
                return self.env[model].browse(self.ids).message_post(
                    body=body, subject=subject, message_type=message_type,
                    subtype=subtype, parent_id=parent_id, attachments=attachments,
                    notif_layout=notif_layout, add_sign=add_sign,
                    mail_auto_delete=mail_auto_delete, model_description=model_description, **kwargs)

        # 0: Find the message's author, because we need it for private discussion
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.env['mail.message']._get_default_author().id

        # 2: Private message: add recipients (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = self.env['mail.message'].browse(parent_id)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 4: mail.message.subtype
        subtype_id = kwargs.get('subtype_id', False)
        if not subtype_id:
            subtype = subtype or 'mt_note'
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and self.ids and partner_ids:
            partner_to_subscribe = partner_ids
            if self._context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = [p for p in partner_ids if
                                        p in self._context.get('mail_post_autofollow_partner_ids')]
            self.message_subscribe(list(partner_to_subscribe))

        # _mail_flat_thread: automatically set free messages to the first posted message
        MailMessage = self.env['mail.message']
        if self._mail_flat_thread and model and not parent_id and self.ids:
            messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model)], order="id ASC",
                                          limit=1)
            parent_id = messages.ids and messages.ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            messages = MailMessage.sudo().search([('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
            # avoid loops when finding ancestors
            processed_list = []
            if messages:
                message = messages[0]
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id

        cc_partner_ids = set()
        cc_recipient_ids = kwargs.pop('cc_recipient_ids', [])
        for partner_id in cc_recipient_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 \
                    and len(partner_id) == 2:
                cc_partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 \
                    and len(partner_id) == 3:
                cc_partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                cc_partner_ids.add(partner_id)
            else:
                pass
        bcc_partner_ids = set()
        bcc_recipient_ids = kwargs.pop('bcc_recipient_ids', [])
        for partner_id in bcc_recipient_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                bcc_partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                bcc_partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                bcc_partner_ids.add(partner_id)
            else:
                pass

        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': model and self.ids[0] or False,
            'body': body,
            'subject': subject or False,
            'message_type': message_type,
            'parent_id': parent_id,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
            'channel_ids': kwargs.get('channel_ids', []),
            'add_sign': add_sign,
            'cc_recipient_ids': [(4, pid.id) for pid in cc_recipient_ids],
            'bcc_recipient_ids': [(4, pid.id) for pid in bcc_recipient_ids]
        })
        if notif_layout:
            values['layout'] = notif_layout

        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        attachment_ids = self._message_post_process_attachments(attachments, kwargs.pop('attachment_ids', []), values)
        values['attachment_ids'] = attachment_ids

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Post the message
        # canned_response_ids are added by js to be used by other computations (odoobot)
        # we need to pop it from values since it is not stored on mail.message
        canned_response_ids = values.pop('canned_response_ids', False)
        new_message = MailMessage.create(values)
        values['canned_response_ids'] = canned_response_ids
        self._message_post_after_hook(new_message, values, model_description=model_description,
                                      mail_auto_delete=mail_auto_delete)
        return new_message
