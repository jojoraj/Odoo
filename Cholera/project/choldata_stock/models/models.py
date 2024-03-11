# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_medicament = fields.Boolean(compute="compute_is_medicamanet")
    brand = fields.Char()
    stock_min = fields.Integer()
    state = fields.Selection([('actif','Actif'),('ordered','En commande'),('out_of_stock','En rupture de stock')], compute="compute_state", store=True, Readonly=False)
    is_expired = fields.Boolean(compute='compute_is_expired')

    @api.depends('categ_id')
    def compute_is_medicamanet(self):
        for rec in self:
            rec.is_medicament = False
            category = self.env.ref('choldata_stock.product_category_medicine')
            if rec.categ_id == category:
                rec.is_medicament = True

    @api.depends('stock_min','qty_available')
    def compute_state(self):
        for rec in self:
            if rec.qty_available >= 3 * rec.stock_min :
                rec.state = 'actif'

    def compute_is_expired(self):
        for rec in self:
            quant_ids = self.env['stock.quant'].search([('product_id.product_tmpl_id','=',rec.id),('lot_id','!=',False),('location_id.usage','=','internal'),('quantity','>',0)])
            rec.is_expired = not any(not quant_id.lot_id.product_expiry_alert for quant_id in quant_ids) if quant_ids else False

    @api.model
    def _alert_stock_min(self):
        product_ids = self.env['product.template'].search([('stock_min','>',0)])
        product_ids = product_ids.filtered(lambda x: x.qty_available <= x.stock_min)
        print(len(product_ids))
        for product_id in product_ids:
            product_id.activity_schedule('choldata_stock.mail_activity_type_alert_stock_min_reached',
                               user_id=self.env.ref('base.user_admin').id,
                               note=_("Niveau de stock critique atteint pour l'intrant %s") % (product_id.display_name))