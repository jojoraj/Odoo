##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    sale_order_origin_id = fields.Many2one(index=True)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    payment_method_ids = fields.Many2many('pos.payment.method', string="Payment method", compute="_compute_methods")
    payment_method = fields.Char(compute="_compute_methods", store=True)

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders, draft)
        order_id = False
        try:
            if len(res) > 0:
                order_id = self.env['pos.order.line'].search([('order_id', '=', res[0]['id'])]).mapped(
                    'sale_order_origin_id')
            if order_id and order_id.opportunity_id:
                order_id.opportunity_id.stage_id = self.env.ref('esanandro_crm.stage_lead6').id
        except Exception as e:
            res = str(e)
            _logger.error("error: %s", res)
        return res

    @api.depends('payment_ids')
    def _compute_methods(self):
        for pay in self:
            pay.payment_method_ids = pay.payment_ids.payment_method_id
            payment_list = []
            payment_method = ""
            for payment in pay.payment_ids:
                if payment_method == "":
                    payment_list.append(payment.payment_method_id.name)
                    payment_method += payment.payment_method_id.name
                else:
                    if payment.payment_method_id.name not in payment_list:
                        payment_method += ", " + payment.payment_method_id.name
                        payment_list.append(payment.payment_method_id.name)
            pay.payment_method = payment_method
