import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class LeadCrm(models.Model):
    _inherit = 'sale.order'

    real_time_wait = fields.Float(tracking=True)
    real_time = fields.Char(string='Temps d\' attente', tracking=True)
    real_price_wait_time = fields.Float(tracking=True)

    def set_real_time_wait(self, *args, **kwargs):
        order_id = self.env['sale.order'].browse(int(kwargs.get('order_id')))
        quantity = kwargs.get('quantity', 0)
        price = kwargs.get('price', 0)
        minutes = float(quantity) % 60
        hours = float(quantity) // 60
        if order_id:
            times = ''
            if hours:
                s = 's' if hours > 1 else ''
                times += f'{int(hours)} heure{s}'
            if minutes:
                s = 's' if minutes > 1 else ''
                times += f' {int(minutes)} minute{s}'
            times_minutes = int(hours) * 60 + int(minutes)
            _logger.info(f'order has been change to: {quantity}, {price}')
            order_id.write({
                'real_time_wait': times_minutes,
                'real_time': times,
                'real_price_wait_time': price
            })
        return True
