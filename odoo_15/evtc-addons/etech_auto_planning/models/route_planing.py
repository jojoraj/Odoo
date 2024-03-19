from odoo import fields, models


class ModelName(models.Model):
    _name = 'planning.route'

    name = fields.Char()
    begin_daily_course = fields.Float(string="Debut du course Journalier")
    end_daily_course = fields.Float(string="Fin du course Journalier")
    active = fields.Boolean(default=False)
