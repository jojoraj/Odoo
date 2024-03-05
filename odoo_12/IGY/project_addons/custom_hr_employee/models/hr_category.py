# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import tools



class EmployeeCategory(models.Model):

    _inherit = "hr.employee.category"
    _order = 'complete_name'
    _rec_name = 'complete_name'

    @api.multi
    def name_get(self):
        res = []
        for category in self:
            name = category.complete_name
            res.append((category.id, name))
        return res
    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )

    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='hr.employee.category',
        ondelete='cascade',
    )
    child_ids = fields.One2many(
        string='Children',
        comodel_name='hr.employee.category',
        inverse_name='parent_id',
    )

    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for group in self:
            if group.parent_id:
                group.complete_name = ('%(parent)s / %(own)s') % ({
                    'parent': group.parent_id.complete_name,
                    'own': group.name,
                })
            else:
                group.complete_name = group.name
