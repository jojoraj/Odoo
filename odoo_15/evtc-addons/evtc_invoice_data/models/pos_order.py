from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_lines(self):
        invoice_lines = super(PosOrder, self)._prepare_invoice_lines()
        for line in self.lines:
            for order_line in line.sale_order_origin_id.order_line:
                if order_line.display_type == 'line_section' and order_line.name:
                    invoice_lines.append((0, None, {
                        'name': order_line.name,
                        'display_type': 'line_section',
                    }))
            break
        return invoice_lines
