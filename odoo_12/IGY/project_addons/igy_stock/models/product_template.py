from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _rec_name = 'name'

    mark = fields.Char(string="Marque")
    model = fields.Char(string="Model")
    serial_number = fields.Char(string="Numero de serie")
    features = fields.Char(string="Caracteristiques")
    stock_name = fields.Char(string="Nom")
    product_type_id = fields.Many2one('product.template.type', string="Type")

    @api.model
    def auto_fill_stock_name(self):
        for product in self.env['product.template'].search([('stock_name', '=', None)]):
            product.stock_name = product.name

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = vals.get('stock_name')
        if not vals.get('stock_name'):
            vals['stock_name'] = vals['name']
        if self._context.get('is_stock'):
            vals['purchase_ok'] = False
            vals['type'] = 'product'
        res = super(ProductTemplate, self).create(vals)
        return res

    def view_product_templates(self):
        action = self.env.ref('igy_stock.action_product_product_igy_view').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        action['context'] = {
            'default_product_tmpl_id': self.id
        }
        return action

    def open_product_template(self):
        action = self.env.ref('igy_stock.action_product_product_igy_view').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        action['context'] = {'is_stock': True, 'default_product_tmpl_id': self.id}
        action['views'] = [
            [self.env.ref('igy_stock.view_product_product_igy_stock_kanban').id, 'kanban'],
            [self.env.ref('igy_stock.view_igy_stock_product_product_form').id, 'form'],
            [self.env.ref('igy_stock.view_igy_stock_product_product_tree').id, 'tree'],
        ]
        return action
