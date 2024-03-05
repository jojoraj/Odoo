
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mark = fields.Char(string="Marque")
    model = fields.Char(string="Model")
    serial_number = fields.Char(string="Numero de serie")
    features = fields.Char(string="Caracteristiques")
    stock_name = fields.Char(string="Nom")
    product_type_id = fields.Many2one('product.template.type', string="Type")
    move_ids = fields.One2many('product.history', 'product_id', string="Historique des mouvements")
    status = fields.Selection([
        ('in_use', "En cours d'utilisation"),
        ('available', "Disponible"),
        ('broken', 'En panne')
    ], string="Satus", default='available')
    employee_id = fields.Many2one('hr.employee', string="Employé")

    @api.onchange('product_tmpl_id')
    def set_values(self):
        for rec in self:
            if rec.product_tmpl_id:
                rec.stock_name = rec.product_tmpl_id.stock_name
                rec.mark = rec.product_tmpl_id.mark
                rec.model = rec.product_tmpl_id.model
                rec.features = rec.product_tmpl_id.features
                rec.product_type_id = rec.product_tmpl_id.product_type_id.id

    @api.model
    def auto_fill_stock_name(self):
        for product in self.env['product.product'].search([('stock_name', '=', None)]):
            product.stock_name = product.name

    @api.model
    def create(self, vals):
        if not vals.get('stock_name'):
            product_tmpl_id = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            vals['stock_name'] = product_tmpl_id.name
            vals['product_type_id'] = product_tmpl_id.product_type_id.id
            vals['mark'] = product_tmpl_id.mark
            vals['model'] = product_tmpl_id.model

        res = super(ProductProduct, self).create(vals)
        return res

    @api.model
    def update_product_state(self):
        product_ids = self.env['product.product'].search([])
        for product in product_ids:
            # if the product has move we update the state depending on the last move or we set the status to available
            if len(product.move_ids) > 0:
                last_move = product.move_ids.sorted(lambda x: x.date)[-1]
                if last_move.type_id.type == 'attribution':
                    product.status = 'in_use'
                    product.employee_id = last_move.employee_id.id
                if last_move.type_id.type == 'restitution':
                    product.status = 'available'
                if last_move.type_id.type == 'broken':
                    product.status = 'broken'
                if last_move.type_id.type == 'return_repair':
                    product.status = 'available'
            else:
                product.status = 'available'

