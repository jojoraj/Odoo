# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil import tz
from datetime import datetime

class BoxResrvation(models.Model):
    _name = 'box.reservation'
    _order = 'time_start DESC'

    name = fields.Many2one("res.users", string=_(
        "Responsable"), required=True, default=lambda self: self.env.uid)
    box_material_id = fields.Many2one(
        'box.material', string=_("Box internet"), required=True)
    time_start = fields.Datetime(string=_("Début"), required=True)
    time_finished = fields.Datetime(String=_("Fin"), required=True)
    description = fields.Text(string=_("Description"))
    timezone_local = fields.Text(string=_("Fuseau horaire"))

    @api.constrains('time_finished')
    def _check_timefinihed(self):
        """Method pour verifier la date de début et date de fin du reservation"""
        timezone_record = self.env['box.timezone'].search([], limit=1)
        timezone_selected = timezone_record.timezone
        timezone_utc = tz.gettz(str(timezone_selected)).utcoffset(datetime.now())
        print(timezone_utc)

        for reservation in self:
            local_timezone = reservation.timezone_local
            local_utc = tz.gettz(str(local_timezone)).utcoffset(datetime.now())
            print(local_utc)
            if timezone_utc != local_utc:
                raise UserError(
                    f"Le fuseau horaire de votre ordinateur est '{local_timezone}' il doit être 'GMT+{timezone_utc}' \nVeuillez configurer le fuseau horaire de votre système.")


            if reservation.time_start > reservation.time_finished:
                raise UserError(
                    _("L'heure du début doit être avant l'heure de la fin."))
            results = self.env["box.reservation"].search([
                ('box_material_id', "=", reservation.box_material_id.id), 
                ('id', "!=", reservation.id), 
                ('time_start', '>=', reservation.time_start), 
                ('time_finished', '<=', reservation.time_finished)
                ]).mapped('id')
            if len(results) > 0:
                raise ValidationError(_("Cette horaire a déjà été pris."))

    @api.model
    def create(self, values):
        if values["name"] != self.env.uid:
            raise UserError(_("Vous devez être le responsable."))
        return super(BoxResrvation, self).create(values)

    @api.multi
    def unlink(self):
        """Method pour empecher les autres utilisateur de supprimer les reservations des autres"""
        for reservation in self:
            if reservation.name.id != self.env.uid:
                raise UserError(
                    _("Vous ne pouvez pas éffacer cette enregistrement."))

        return super(BoxResrvation, reservation).unlink()

    @api.multi
    def write(self, values):
        """Method pour empecher les autres utilisateur de modifier les reservations des autres"""
        if self.name != self.env.user:
            raise UserError(
                _("Vous ne pouvez pas modifier cette enregistrment."))

        return super(BoxResrvation, self).write(values)
