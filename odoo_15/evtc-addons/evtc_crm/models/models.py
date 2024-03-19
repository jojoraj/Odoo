from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EvtcCrm(models.Model):
    _inherit = 'crm.lead'

    is_location = fields.Boolean(string='Location')
    location_duration = fields.Many2one('price.location', string="Durée de la location")
    as_many_course = fields.Boolean(string="Plusieurs courses")
    others_destination = fields.One2many('crm.lead.course', 'lead_id', string="Zone de remisage")
    out_tana = fields.Boolean(string='location out of Tana')

    @api.constrains('as_many_course', 'others_destination')
    def _constrains_as_many_course(self):
        if any(rec.as_many_course and len(rec.others_destination) < 2 for rec in self):
            raise ValidationError(_('Veuillez ajouter au moins 2 destinations'))


class EvtcManyCourse(models.Model):
    _name = 'crm.lead.course'

    lead_id = fields.Many2one('crm.lead')
    name = fields.Text(string="Lieu")
    delay = fields.Boolean(string="Temps d'attente")
    kilometers_estimted = fields.Float(string="Kilometre estimée")
    coordinate = fields.Char()
    latitude = fields.Char()
    longitude = fields.Char()
