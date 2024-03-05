# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, UserError


class AlterningMailServer(models.Model):
    _name = 'alterning.mail.server'

    name = fields.Char(string=_("Alterning mail server name"))
    in_use = fields.Boolean(string=_("In use"), default=True)
    alterning_line_ids = fields.One2many('alterning.mail.server.line', 'alterning_id', string=_("Alterning current"))
    number_server_to_use = fields.Integer(string=_("Number server to use"), default=1)
    autorize_server_choice = fields.Boolean(string=_("Autorize server mail choice"), default=True)

    def disable_alterning_mail_server(self):
        for line in self:
            if line.in_use:
                line.in_use = False

    def enable_alterning_mail_server(self):
        for line in self:
            if line.in_use == False:
                line.in_use = True

    @api.model
    def execute_alterning_mail_server(self):
        try:
            ir_mail_server_env = self.env['ir.mail_server']
            alterning_mail_server_env = self.env['alterning.mail.server']
            alterning_mail_server_line_env = self.env['alterning.mail.server.line']
            alterning_mail_server_record = self.env.ref('igy_alterning_mail_server.alterning_mail_server_record')
            if alterning_mail_server_record.in_use:
                all_active_mail_server_ids = ir_mail_server_env.sudo().search(
                             [('active', '=', True)])
                mail_server_to_add = []
                list(map(lambda server: mail_server_to_add.append(
                    server.id) if alterning_mail_server_env.test_current_mail_server(server) else False,
                         all_active_mail_server_ids))

                ir_mail_server_ids = ir_mail_server_env.sudo().browse(mail_server_to_add)
                alterning_line_ids = []

                list(map(lambda alterning: alterning.sudo().update({'is_current_server': False}),
                         alterning_mail_server_line_env.sudo().search(
                             [('alterning_id', '=', alterning_mail_server_record.id)])))
                list(map(lambda alterning: alterning.sudo().unlink(),
                         alterning_mail_server_line_env.sudo().search(
                             [('name', '=', False)])))
                if len(ir_mail_server_ids.mapped('id')) == len(alterning_mail_server_record.alterning_line_ids.mapped('id')):
                    list(map(lambda alterning_line: alterning_line.sudo().unlink(),
                             alterning_mail_server_record.alterning_line_ids))
                else:
                    for line_server in ir_mail_server_ids.filtered(lambda x: x.id not in alterning_mail_server_record.alterning_line_ids.mapped('name.id')):
                        if len(alterning_line_ids) < alterning_mail_server_record.number_server_to_use:
                            alterning_mail_server_line_env.sudo().create({
                                'name': line_server.id,
                                'is_current_server': True,
                                'alterning_id': alterning_mail_server_record.id
                            })
                            alterning_line_ids.append(line_server.id)

                if len(alterning_line_ids) < alterning_mail_server_record.number_server_to_use:
                    for line_server in ir_mail_server_ids:
                        if line_server.id not in alterning_mail_server_record.alterning_line_ids.mapped('name.id'):
                            if len(alterning_line_ids) < alterning_mail_server_record.number_server_to_use:
                                alterning_mail_server_line_env.sudo().create({
                                    'name': line_server.id,
                                    'is_current_server': True,
                                    'alterning_id': alterning_mail_server_record.id
                                })
                                alterning_line_ids.append(line_server.id)
                        else:
                            if len(alterning_line_ids) < alterning_mail_server_record.number_server_to_use:
                                for alterning_mail_server_line in alterning_mail_server_record.alterning_line_ids.filtered(
                                        lambda x: x.name.id == line_server.id):
                                    alterning_mail_server_line.update({
                                        'is_current_server': True
                                    })
                                    alterning_line_ids.append(line_server.id)
        except:
            pass

    def test_current_mail_server(self, server):
        test = True
        smtp = False
        ir_mail_server_env = self.env['ir.mail_server']
        try:
            smtp = ir_mail_server_env.connect(mail_server_id=server.id)
            # simulate sending an email from current user's address - without sending it!
            email_from, email_to = self.env.user.email, 'noreply@odoo.com'
            if not email_from:
                test = False
            # Testing the MAIL FROM step should detect sender filter problems
            (code, repl) = smtp.mail(email_from)
            if code != 250:
                test = False
            # Testing the RCPT TO step should detect most relaying problems
            (code, repl) = smtp.rcpt(email_to)
            if code not in (250, 251):
                test = False
            # Beginning the DATA step should detect some deferred rejections
            # Can't use self.data() as it would actually send the mail!
            smtp.putcmd("data")
            (code, repl) = smtp.getreply()
            if code != 354:
                test = False
        except UserError as e:
            # let UserErrors (messages) bubble up
            test = False
        except Exception as e:
            test = False
        finally:
            try:
                if smtp:
                    smtp.close()
            except Exception:
                # ignored, just a consequence of the previous exception
                pass
        return test
