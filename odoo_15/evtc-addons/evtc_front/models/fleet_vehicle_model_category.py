from datetime import datetime

from odoo import api, models, tools


def str_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def get_format_amount(env, amount, currency, lang_code=False):
    fmt = "%.{}f".format(0)
    lang = tools.get_lang(env, lang_code)

    formatted_amount = lang.format(fmt, currency.round(amount), grouping=True, monetary=True) \
        .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

    pre = post = u''
    if currency.position == 'before':
        pre = u'{NO-BREAK SPACE}'
    else:
        post = u'\N{NO-BREAK SPACE}%s' % currency.symbol or ''

    return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)


class FleetVehicleModelCategory(models.Model):
    _inherit = 'fleet.vehicle.model.category'
    _description = """
        get working vehicle price with date
    """

    @api.model
    def get_vehicle_price_per_km(self, *args, **kwargs):
        if not kwargs.get('recuperation'):
            return {}
        recuperation = str_to_time(kwargs.get('recuperation'))
        day = recuperation.strftime("%w")
        day_spring = (int(day) - 1) % 7
        float_hours = recuperation.time().hour + (recuperation.time().minute / 100)
        values = {}
        for vehicle in self.sudo().search([], order='qualification_level'):
            vehicle_found = vehicle.list_price.filtered(
                lambda l: not l.is_location and l.resource_calendar_id.attendance_ids.filtered(
                    lambda w: w.dayofweek in [str(day_spring),
                                              int(day_spring)] and w.hour_from <= float_hours <= w.hour_to
                ))
            currency = self.env.user.company_id.currency_id
            vehicle_found = vehicle_found[-1] if len(vehicle_found) > 1 else vehicle_found
            price = vehicle_found.product_id.list_price if vehicle_found else vehicle.tarif
            values[vehicle.id] = get_format_amount(self.env, price, currency)
        return values

    @api.model
    def get_first_game_id(self, *args, **kwargs):
        category_ids = self.sudo().search([], order='qualification_level')
        return category_ids[0].id if category_ids else None
