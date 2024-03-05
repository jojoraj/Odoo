from odoo import fields, models


class MailReporting(models.Model):
    _name = "mail.mail_reporting"
    _description = "Mail Mail Reporting"

    opened = fields.Integer(string="Ouvré")
    clicked = fields.Integer(string="Cliqué")
    bounced = fields.Integer(string="Rebondi")
    sent_date = fields.Datetime(string='Sent Date')
