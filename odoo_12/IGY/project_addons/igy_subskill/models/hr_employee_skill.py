# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
class Igy_subskill(models.Model):
    _inherit = 'hr.employee.skill'

    skill_id = fields.Many2one(
        string='Skill',
        comodel_name='hr.skill',
        domain=[('parent_id','=',None)],
    )
    igy_skill_ids = fields.Many2many('hr.skill','skill_subskill_rel', 'rel_skill_id', 'rel_sub_skill_id')

    @api.onchange('skill_id')
    def onchange_skill_id(self):
        for rec in self:
            return {'domain':{'igy_skill_ids':[('id','in',rec.skill_id.child_ids.ids)]}}

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s' % (rec.skill_id)))
        return res

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100):
    #     if args is None:
    #         args = []
    #     domain = args + ['|', ('model',operator,name)]
    #     return(Igy_subskill,self).search(domain,limit=limit).name_get()

    # @api.model
    # def skill_filter(self):
    #     args = []



class Employee(models.Model):
    _inherit = 'hr.employee'


    sub_skill_ids = fields.Many2many(
        'hr.skill', 
        related='employee_skill_ids.igy_skill_ids'
    )
    competence_skill_ids = fields.Many2one(
        'hr.skill', 
        related = 'employee_skill_ids.skill_id'
        
    )


    
    








