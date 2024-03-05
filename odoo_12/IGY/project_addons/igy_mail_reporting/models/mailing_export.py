from odoo import fields, models


class mailingExport(models.Model):
    _name = "crm.mail.export"

    date = fields.Date(string="Exporter", default=fields.Date.today())
    name = fields.Char(string="Nom")

