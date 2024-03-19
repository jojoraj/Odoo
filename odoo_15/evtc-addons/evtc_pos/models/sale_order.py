from datetime import datetime

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def set_order_start_datetime(self, *args, **kwargs):
        self.order_start_date = datetime.utcnow()
        return True

    def set_order_stop_datetime(self, *args, **kwargs):
        self.order_stop_date = datetime.utcnow()
        self.real_cost = float(kwargs.get('amount', 0))
        return True
