# -*- coding: utf-8 -*-

import datetime
from dateutil import tz
from pytz import timezone
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError


class Reservation(models.Model):
    _name = "meeting.reservation"

    name = fields.Char(string="Titre de la réunion", required=True)
    meeting_room_id = fields.Many2one('meeting.room', string="Salle de réunion", required=True)
    user_id = fields.Many2one("res.users", string="Responsable", required=True, default=lambda self: self.env.uid)
    time_start = fields.Datetime(string="Début", required=True)
    time_finished = fields.Datetime(String="Fin", required=True)
    description = fields.Text(string="Description")
    obligatory_ids = fields.Many2many("hr.employee", "meeting_obligatory_rel", string="Présence obligatoire")
    optional_ids = fields.Many2many("hr.employee", "meeting_optional_rel", string="Présence facultatif")
    reminder_sent = fields.Boolean(string="Rappel envoyée", default=False)
    timezone_local = fields.Char(string="Fuseau horaire")

    @api.model
    def set_reminder(self):
        for rec in self:
            rec.reminder_sent = True
        return True

    @api.model
    def create(self, values):
        if values["user_id"] != self.env.uid:
            raise UserError("Vous devez être le responsable.")

        res = super(Reservation, self).create(values)
        mail_obj = self.env['mail.mail']

        body_html = "<p>Vous êtes convié à la réunion <b>\"" + res.name + "\"</b> par " + res.user_id.name + "</p>" \
                                                                                                             "<p STYLE='padding:0 0 0 30px;'>Date : le " + res.time_start.strftime(
            "%d/%m/%Y") + "</p>" \
                          "<p STYLE='padding:0 0 0 30px;'>Horaire :  de " + res.time_start.astimezone(
            timezone('Indian/Antananarivo')).strftime("%H:%M") + " à " + res.time_finished.astimezone(
            timezone('Indian/Antananarivo')).strftime("%H:%M") + "</p> " \
                                                                 "<p STYLE='padding:0 0 0 30px;'>Lieu : " + res.meeting_room_id.name + "</p><br> "

        if res.description not in [None, False, '']:
            body_html += "<p>" + res.description + "</p>"

        if len(res.obligatory_ids) > 0:
            body_html += "<ul> Les employées dont la présence est obligatoire sont :"
            for hr in res.obligatory_ids:
                body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
            body_html += "</ul><br>"
        if len(res.optional_ids) > 0:
            body_html += "<ul> Les employées dont la présence est optionnelle sont :"
            for hr in res.optional_ids:
                body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
            body_html += "</ul><br>"

        mail_to = ','.join([x.work_email for x in res.obligatory_ids] + [x.work_email for x in res.obligatory_ids])

        mail = mail_obj.create({
            'subject': f"INGENOSYA | Création de la réunion réunion({res.name})",
            'body_html': body_html,
            'email_from': 'contact@ingenosya.mg',
            'auto_delete': True,
            'email_to': mail_to,
            'state': 'outgoing',
            'notif_layout': 'mail.mail_notification_light',
        })
        mail.send()
        return res

    @api.constrains('time_finished', 'obligatory_ids', 'optional_ids')
    def _check_timefinihed(self):

        # Fuseau horaire  sélectionné dans la configuration
        timezone_record = self.env['meeting.timezone'].search([], limit=1)
        timezone_selected = timezone_record.timezone
        timezone_utc = tz.gettz(str(timezone_selected)).utcoffset(datetime.datetime.utcnow())

        for reservation in self:
            # Fuseau horaire sur PC de l'utilisateur
            local_timezone = reservation.timezone_local
            local_utc = tz.gettz(str(local_timezone)).utcoffset(datetime.datetime.utcnow())

            if local_utc != timezone_utc:
                raise UserError(
                    f"Le fuseau horaire de votre ordinateur est '{local_timezone}' il doit être en 'GMT+{timezone_utc}'. \nVeuillez configurer le fuseau horaire de votre système.")

            if reservation.time_start > reservation.time_finished:
                raise UserError("L'heure du début doit être avant l'heure de la fin.")
            results = self.env["meeting.reservation"].search([
                ('meeting_room_id', "=", reservation.meeting_room_id.id),
                ('id', "!=", reservation.id),
                ('time_start', '>=', reservation.time_start),
                ('time_finished', '<=', reservation.time_finished)
            ]).mapped('id')
            if len(results) > 0:
                raise ValidationError("Cette horaire a déjà été pris.")
            for line_id in reservation.obligatory_ids.mapped('id'):
                if line_id in reservation.optional_ids.mapped('id'):
                    raise UserError(
                        "Il est impossible de rendre la présence des employés à la fois obligatoire et optionnelle!")

    @api.multi
    def unlink(self):
        for reservation in self:
            if reservation.user_id.id != self.env.uid:
                raise UserError("Vous ne pouvez pas éffacer cette enregistrement.")
            mail_obj = self.env['mail.mail']

            body_html = "<p>La réunion <b>\"" + self.name + "\"</b> où vous avez été convié par " + self.user_id.name + " a été Annulée</p>"

            mail_to = ','.join(
                [x.work_email for x in self.obligatory_ids] + [x.work_email for x in self.obligatory_ids])

            mail = mail_obj.create({
                'subject': f"INGENOSYA | Annulation de la réunion réunion({self.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to': mail_to,
                'state': 'outgoing',
                'notif_layout': 'mail.mail_notification_light',
            })
            super(Reservation, reservation).unlink()
            mail.send()
        return True

    @api.multi
    def write(self, values):
        if self.user_id != self.env.user:
            raise UserError("Vous ne pouvez pas modifier cette enregistrment.")

        if values.get("user_id"):
            if values["user_id"] != self.env.user.id:
                print(values["user_id"], self.env.user.id)
                print("""
                9a peut aller
                """)
                raise ValidationError("Vous devez être responsable.")
        result = super(Reservation, self).write(values)

        if values.get('reminder_sent') == True:
            return result

        mail_obj = self.env['mail.mail']

        body_html = "<p>La réunion <b>\"" + self.name + "\"</b> où vous avez été convié par " + self.user_id.name + " a été modififiée</p>" \
                                                                                                                    "<p STYLE='padding:0 0 0 30px;'>Date : le " + self.time_start.strftime(
            "%d/%m/%Y") + "</p>" \
                          "<p STYLE='padding:0 0 0 30px;'>Horaire :  de " + self.time_start.astimezone(
            timezone('Indian/Antananarivo')).strftime("%H:%M") + " à " + self.time_finished.astimezone(
            timezone('Indian/Antananarivo')).strftime("%H:%M") + "</p> => " \
                                                                 "<p STYLE='padding:0 0 0 30px;'>Lieu : " + self.meeting_room_id.name + "</p><br> "

        if self.description not in [None, False, '']:
            body_html += "<p>" + self.description + "</p>"

        if len(self.obligatory_ids) > 0:
            body_html += "<ul> Les employées dont la présence est obligatoire sont :"
            for hr in self.obligatory_ids:
                body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
            body_html += "</ul><br>"
        if len(self.optional_ids) > 0:
            body_html += "<ul> Les employées dont la présence est optionnelle sont :"
            for hr in self.optional_ids:
                body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
            body_html += "</ul>"

        mail_to = ','.join([x.work_email for x in self.obligatory_ids] + [x.work_email for x in self.obligatory_ids])

        mail = mail_obj.create({
            'subject': f"INGENOSYA | Modification de la réunion réunion({self.name})",
            'body_html': body_html,
            'email_from': 'contact@ingenosya.mg',
            'auto_delete': True,
            'email_to': mail_to,
            'state': 'outgoing',
            'notif_layout': 'mail.mail_notification_light',
        })
        mail.send()

        return result

    @api.model
    def meeting_reminder(self):
        reservation_obj = self.env['meeting.reservation']
        for res in reservation_obj.search(
                [('time_start', '>=', datetime.datetime.today() - datetime.timedelta(minutes=5)),
                 ('time_start', '<=', datetime.datetime.today() + datetime.timedelta(minutes=30)),
                 ('reminder_sent', '=', False)]):
            mail_obj = self.env['mail.mail']

            body_html = "<p>Vous êtes convié à la réunion <b>\"" + res.name + "\"</b> par " + res.user_id.name + "</p>" \
                                                                                                                 "<p STYLE='padding:0 0 0 30px;'>Date : le " + res.time_start.strftime(
                "%d/%m/%Y") + "</p>" \
                              "<p STYLE='padding:0 0 0 30px;'>Horaire :  de " + res.time_start.astimezone(
                timezone('Indian/Antananarivo')).strftime("%H:%M") + " à " + res.time_finished.astimezone(
                timezone('Indian/Antananarivo')).strftime("%H:%M") + "</p> " \
                                                                     "<p STYLE='padding:0 0 0 30px;'>Lieu : " + res.meeting_room_id.name + "</p><br> "
            if res.description not in [None, False, '']:
                body_html += "<p>" + res.description + "</p>"

            if len(res.obligatory_ids) > 0:
                body_html += "<ul> Les employées dont la présence est obligatoire sont :"
                for hr in res.obligatory_ids:
                    body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
                body_html += "</ul><br>"
            if len(res.optional_ids) > 0:
                body_html += "<ul> Les employées dont la présence est optionnelle sont :"
                for hr in res.optional_ids:
                    body_html += "<li STYLE='padding:0 0 0 30px;'>" + hr.name + "</li>"
                body_html += "</ul><br>"

            mail_to = ','.join([x.work_email for x in res.obligatory_ids] + [x.work_email for x in res.obligatory_ids])

            mail = mail_obj.create({
                'subject': f"INGENOSYA | Rappel de la réunion({res.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to': mail_to,
                'state': 'outgoing',
                'notif_layout': 'mail.mail_notification_light',
            })
            mail.send()
            res.set_reminder()
        return True
