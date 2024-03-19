import logging
import math

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AreaField(models.Model):
    _inherit = 'crm.lead.course'

    wait_time = fields.Many2one('area.time.wait', string="Temps d'attente")
    kilometers_real = fields.Char(string="Kilometre éstimatif")


def get_short_tm(tm, h=False):
    return f"{str(int(tm)).zfill(2)} {_('h') if h else _('mn')}" if tm else ''


def real_times_abr(hour, minutes):
    return f"{get_short_tm(hour, h=True)} {get_short_tm(minutes)}"


def convert_time_plural(time=0):
    return 's' if time > 1 else ''


def float_time_convert(times):
    factor, val = times < 0 and -1 or 1, abs(times)
    return factor * int(math.floor(val)), int(round((val % 1) * 60))

    # hour, minute = self.float_time_convert(self.duration)


def get_current_time(tm, h=False):
    return f"{str(int(tm)).zfill(2)} {_('hour') if h else _('minute')}{convert_time_plural(int(tm))}" if tm else ''


class AreaDestination(models.Model):
    _name = 'area.time.wait'

    name = fields.Char(store=True)
    real_time = fields.Char(string="Duration")
    wait_time_float = fields.Float(store=True)
    waiting_price = fields.Float(string="Price")
    active = fields.Boolean(string='active', default=True)
    wait_time_mn = fields.Integer(string="Convert time minutes")

    @api.onchange('wait_time_float')
    def _onchange_wait_time_mn(self):
        for record in self:
            h, m = float_time_convert(record.wait_time_float)
            # data = [float(x) for x in str(record.wait_time_float).split('.') if record.wait_time_float ]
            if h or m:
                w_mn = int(h) * 60 + int(m)
                area_time_price = self.env['area.time.wait.price'].search([
                    ('begin_wait_time', '<', w_mn),
                    ('end_wait_time', '>=', w_mn),
                    ('active', '=', True),
                ])
                record.sudo().write({
                    'wait_time_mn': w_mn,
                    'real_time': f"{real_times_abr(h, m)}",
                    'waiting_price': area_time_price and area_time_price.price or 0
                })
                record.name = f"{self.real_times(h, m)}"

    @staticmethod
    def real_times(hour, minutes):
        return f"{get_current_time(hour, h=True)} {get_current_time(minutes)}"

    def get_price_unit(self, *args, **kwargs):
        mins = kwargs.get('min')
        area = self.env['area.time.wait.price'].sudo().search([
            ('begin_wait_time', '<', mins),
            ('end_wait_time', '>=', mins),
            ('active', '=', True),
        ])
        own_price = area and area.price or 0
        _logger.info(f"price time return: {own_price}")
        return own_price


class PriceWaitTime(models.Model):
    _name = 'area.time.wait.price'

    name = fields.Char()
    begin_wait_time = fields.Integer()
    end_wait_time = fields.Integer()
    price = fields.Float()
    active = fields.Boolean(default=True)

    @api.onchange('begin_wait_time', 'end_wait_time')
    def onchange_time(self):
        if self.begin_wait_time or self.end_wait_time:
            self.name = f'Intervalle de temps entre {self.begin_wait_time} - {self.end_wait_time} minutes'
        else:
            self.name = ''
