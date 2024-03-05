# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplateCustoms(models.Model):
    _inherit = "product.template"

    principal_seller = fields.Char("Fournisseur", compute="_compute_principal_seller")
    principal_price = fields.Float("Prix", compute="_compute_principal_seller")

    @api.multi
    def _compute_principal_seller(self):
        for rec in self:
            if len(rec.seller_ids) == 0:
                rec.principal_seller = ''
                rec.principal_price = 0.0
            else:
                price = min(rec.seller_ids.mapped('price'))
                sellers = rec.seller_ids.filtered(lambda x: x.price == price)
                rec.principal_seller = sellers[0].name.name
                rec.principal_price = price