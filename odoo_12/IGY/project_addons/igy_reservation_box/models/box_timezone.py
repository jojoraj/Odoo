# -*- coding: utf-8 -*-
from odoo import fields, models, api
import pytz


class BoxTimezone(models.Model):
    _name = 'box.timezone'
    _description = 'Configuration time zone'

    timezone = fields.Selection([(tz, tz) for tz in pytz.all_timezones], string="Fuseau horaire")
