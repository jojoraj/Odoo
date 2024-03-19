from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_type = fields.Selection(related='partner_id.company_type', store=True)


class SaleReport(models.Model):
    _inherit = "sale.report"

    company_type = fields.Selection([
        ('person', _('Personal')),
        ('company', _('Society')),
    ], string='Client type', readonly=True)

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        fields = fields if fields else []
        fields['company_type'] = ", s.company_type as company_type"
        groupby += ", s.company_type"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
