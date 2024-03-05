# -*- coding: utf-8 -*-
from odoo import fields, api, models
import pytz

class MeetingTimezone(models.Model):
    _name = 'meeting.timezone'
    _description = 'Configuration Time zone'

    timezone = fields.Selection([(tz, tz) for tz in pytz.all_timezones], string="Fuseau horaire")
