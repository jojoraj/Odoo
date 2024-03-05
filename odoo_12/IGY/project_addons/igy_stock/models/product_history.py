
from odoo import api, fields, models


class ProductHistory(models.Model):
    _name = 'product.history'

    date = fields.Date(string="Date", default=fields.Date.today())

    type_id = fields.Many2one('product.history.type', string="Motif")
    type = fields.Selection([
        ('attribution', 'Attribution'),
        ('restitution', 'Restitution'),
        ('broken', 'En panne'),
        ('return_repair', 'Retour de réparation')
    ], related='type_id.type')
    employee_id = fields.Many2one('hr.employee', string="Employee", domain="['|', ('active', '=', True), ('active', '=', False)]")
    code = fields.Char(string="Pin / Code barre")
    product_id = fields.Many2one('product.product')

    @api.onchange('code', 'employee_id')
    def change_code(self):
        for rec in self:
            if rec.employee_id:
                rec.code = ''
                rec.code = rec.employee_id.pin

            # if rec.code:
            #     employee_id = self.env['hr.employee'].search([
            #         '|', ('pin', '=', rec.code), ('barcode', '=', rec.code)
            #     ], limit=1)
            #     if rec.employee_id:
            #         if employee_id.id != rec.employee_id.id:
            #             rec.code = ''
            #             warning = {
            #                 'title': ('Warning!'),
            #                 'message': ('Pin ou badge incorrect'),
            #             }
            #             return {'warning': warning}
            #     if not rec.employee_id:
            #         if employee_id:
            #             rec.employee_id = employee_id.id
            #         else:
            #             rec.code = ''
            #             warning = {
            #                 'title': ('Warning!'),
            #                 'message': ('Employe non trouve'),
            #             }
            #             return {'warning': warning}

    @api.model
    def create(self, vals):
        res = super(ProductHistory, self).create(vals)
        self.update_history(type_id=res.type_id, product_history_id=res)
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductHistory, self).write(vals)
        if vals.get('type_id') or vals.get('date'):
            type_id = vals.get('type_id', False) or self.type_id.id
            type_id = self.env['product.history.type'].browse(type_id)
            self.update_history(type_id=type_id, product_history_id=self)
        return res

    def update_history(self, type_id, product_history_id):
        type_values = ('attribution', 'restitution', 'broken', 'return_repair')
        if type_id.type in type_values:
            move_ids = product_history_id.product_id.move_ids.sorted(lambda move: move.date).filtered(
                lambda move: move.type_id.type in type_values)
            if len(move_ids) > 0:
                last_move = move_ids[-1]
                if last_move.id == product_history_id.id:
                    if product_history_id.type_id.type == 'attribution':
                        product_history_id.product_id.status = 'in_use'
                        product_history_id.product_id.employee_id = last_move.employee_id.id
                    if product_history_id.type_id.type == 'restitution':
                        product_history_id.product_id.status = 'available'
                    if product_history_id.type_id.type == 'broken':
                        product_history_id.product_id.status = 'broken'
                    if product_history_id.type_id.type == 'return_repair':
                        product_history_id.product_id.status = 'available'

