# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, UserError


class AlterningMailServerLine(models.Model):
    _name = 'alterning.mail.server.line'

    name = fields.Many2one('ir.mail_server', string=_("Mail server"))
    smtp_host = fields.Char(string='SMTP Server', required=True, help="Hostname or IP of SMTP server", related="name.smtp_host")
    smtp_port = fields.Integer(string='SMTP Port', size=5, required=True, default=25,
                               help="SMTP Port. Usually 465 for SSL, and 25 or 587 for other cases.", related="name.smtp_port")
    alterning_id = fields.Many2one('alterning.mail.server', string=_("Alterning"))
    is_current_server = fields.Boolean(string=_("Is current server"))
