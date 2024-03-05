# -*- coding: utf-8 -*-

from odoo import models,fields,api
class ProjectInherit(models.Model):
    _inherit="project.project"

    @api.depends('percentage_finished')
    def _compute_stage(self):
        for projet in self: 
            stage,color = 1,0
            if projet.percentage_finished == 0 :
                stage = self.env['project.project.stage'].search([('state','=','new')], limit=1)
                color = 0
            elif projet.percentage_finished > 0 and projet.percentage_finished <81:
                stage = self.env['project.project.stage'].search([('state','=','open')], limit=1)
                color = 10
            elif projet.percentage_finished > 80 and projet.percentage_finished <101:
                stage = self.env['project.project.stage'].search([('state','=','done')], limit=1)
                color = 2
            elif projet.percentage_finished > 100  :
                stage = self.env['project.project.stage'].search([('state','=','cancel')], limit=1)
                color = 1
            projet.stage_id = stage
            projet.color_kanban = color

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)   
    stage_id = fields.Many2one(
        'project.project.stage',
        compute = '_compute_stage',
        group_expand='_group_expand_stage_id',
        store=True,  
    )
    color_kanban = fields.Integer(
        string='Color ',
        store = True,
        compute = '_compute_stage',
        default = 0
    )
    state = fields.Selection(related='stage_id.state') 





