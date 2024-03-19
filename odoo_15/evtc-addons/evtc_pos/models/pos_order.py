from odoo import models, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.constrains('state')
    def check_order_state(self):
        for rec in self:
            if rec.state in ['done', 'invoiced'] and rec.sale_order_count > 0:
                sale_order_ids = self.env['sale.order'].search([('pos_order_line_ids', 'in', rec.mapped('lines').ids)])
                if sale_order_ids:
                    for sale_order_id in sale_order_ids:
                        sale_order_id.real_cost = rec.amount_paid
