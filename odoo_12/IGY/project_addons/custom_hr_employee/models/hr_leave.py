import math

from odoo import api, fields, models
from odoo.exceptions import ValidationError



class HrLeave(models.Model):
    _inherit = 'hr.leave'

    project_name_search = fields.Char(string="Projet")

    @api.onchange('request_hour_from', 'request_hour_to')
    def on_change_date_work(self):
        for rec in self:
            if rec.employee_id:
                working_days = rec.employee_id.resource_calendar_id
                date_employee_leave = rec.request_date_from
                week_day = date_employee_leave.weekday()
                working_hour = working_days.attendance_ids.filtered(lambda x: int(x.dayofweek) == week_day)

                if working_hour:
                    request_hour_from = 0
                    request_hour_to = 0
                    if rec.request_hour_from:
                        request_hour_from = math.fabs(int(rec.request_hour_from)) - 0.5 if int(rec.request_hour_from) < 0 else int(rec.request_hour_from)
                    if rec.request_hour_to:
                        request_hour_to = math.fabs(int(rec.request_hour_to)) - 0.5 if int(rec.request_hour_to) < 0 else int(rec.request_hour_to)

                    morning_begin_calendar = working_hour[0].hour_from
                    morning_end_calendar = working_hour[0].hour_to
                    afternoon_begin_calendar = working_hour[1].hour_from
                    afternoon_end_calendar = working_hour[1].hour_to

                    if request_hour_from:
                        if morning_begin_calendar <= request_hour_from <= morning_end_calendar or afternoon_begin_calendar <= request_hour_from <= afternoon_end_calendar:
                            pass
                        else:
                            raise ValidationError("L'heure de début n'est pas comprise dans les heures de travail")

                    if request_hour_to:
                        if morning_begin_calendar <= request_hour_to <= morning_end_calendar or afternoon_begin_calendar <= request_hour_to <= afternoon_end_calendar:
                            pass
                        else:
                            raise ValidationError("L'heure de fin n'est pas comprise dans les heures de travail")

