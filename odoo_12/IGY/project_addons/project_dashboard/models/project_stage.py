from odoo import fields, models


class ProjectStage(models.Model):
    _name = 'project.project.stage'
    _description = 'Project Stage'
    _order = 'sequence,name'

    name = fields.Char(translation=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    fold = fields.Boolean()
    state = fields.Selection(
        [
            ('new','New'),
            ('open','Borrowed'),
            ('done','Returned'),
            ('cancel', 'Cancelled')
        ],
        default='new',
    )
    
