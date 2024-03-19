from odoo import models


class ModelName(models.Model):
    _inherit = 'res.currency'
    _description = 'return object currency'

    def get_unit_per_mga(self, **kwargs):
        """
        params: none
        return:
        --------------------
            value of one dollar and one euro
        """
        rateUSD = self.env['res.currency.rate'].search([('currency_id', '=', self.env.ref('base.USD').id)], order='name DESC', limit=1)
        rateEUR = self.env['res.currency.rate'].search([('currency_id', '=', self.env.ref('base.EUR').id)], order='name DESC', limit=1)
        one_usd = (rateUSD) and rateUSD.company_rate or None
        one_eur = (rateEUR) and rateEUR.company_rate or None
        return {'usd': one_usd, 'eur': one_eur}
