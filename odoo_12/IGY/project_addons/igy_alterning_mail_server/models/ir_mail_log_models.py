# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrMailLog(models.Model):
    _name = 'ir.mail.log'

    name = fields.Many2one('ir.mail_server', string=_("Mail server"))
    email_to = fields.Char(string=_("Email to"))
    date = fields.Date(string=_("Date"))

    @api.model
    def execute_mail_log_to_mail(self):
        try:
            mail_log_ids = self.env['ir.mail.log'].sudo().search([])
            mail_obj = self.env['mail.mail']
            ir_mail_log_config_data = self.env.ref('igy_alterning_mail_server.ir_mail_log_config_data')

            body_html = "<p>Détails de la liste des emails envoyés:</p><br>"
            body_html += """
                    <table cellspacing="3" bgcolor="#000000">
                    <tr bgcolor="#ffffff">
                    <th>Server mail name</th>
                    <th>Server mail host</th>
                    <th>Email to</th>
                    <th>Date</th>
                    </tr>
                    """
            for line in mail_log_ids:
                body_html += """
                                <tr bgcolor="#ffffff">
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                                <td>{3}</td>
                                </tr>
                                """.format(line.name.name, line.name.smtp_host, line.email_to, line.date)
            body_html += """
                            <table>
                            """
            list(map(lambda mail_log: mail_log.sudo().unlink(), mail_log_ids))
            email_list = ir_mail_log_config_data.email_ids.mapped('name')
            mail_to = ','.join(email_list)

            mail = mail_obj.create({
                'subject': "Détails de la liste des emails envoyés",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to': mail_to,
                'state': 'outgoing',
                'notif_layout': 'mail.mail_notification_light',
            })
            mail.send()
        except:
            pass

class IrMailLogConfig(models.Model):
    _name = 'ir.mail.log.config'

    name = fields.Char(string=_("Email to send mail log details"))
    email_ids = fields.One2many('ir.mail.log.config.line', 'config_id', string=_("Email"))


class IrMailLogConfigLine(models.Model):
    _name = 'ir.mail.log.config.line'

    name = fields.Char(string=_("Email"))
    config_id = fields.Many2one('ir.mail.log.config', string=_("Config"))

