# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SanitaryBarrier(models.Model):
    _name = 'sanitary.barrier'

    name = fields.Char()
    
    street = fields.Char()
    province_id = fields.Many2one('res.province', string='Province')
    region_id = fields.Many2one('res.region', string='Région', domain=[('id', 'in', [])])
    district_id = fields.Many2one('res.district', string='District', domain=[('id', 'in', [])])
    commune_id = fields.Many2one('res.commune', string='Commune', domain=[('id', 'in', [])])
    fkt = fields.Many2one('x_fokontany', string='Fokontany', domain=[('id', 'in', [])])
    kilometre_marker = fields.Char()
    responsible = fields.Many2one('res.partner')
    team_ids = fields.Many2many('res.partner')
    
    
    
    @api.onchange('province_id')
    def _onchange_province_id(self):
        if self.province_id:
            return {'domain': {'region_id': [('id', 'in', self.province_id.region_ids.ids)]}}
        else:
            return {'domain': {'region_id': []}}

    @api.onchange('region_id')
    def _onchange_region_id(self):
        if self.region_id:
            return {'domain': {'district_id': [('id', 'in', self.region_id.district_ids.ids)]}}
        else:
            return {'domain': {'district_id': []}}

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id:
            return {'domain': {'commune_id': [('id', 'in', self.district_id.commune_ids.ids)]}}
        else:
            return {'domain': {'commune_id': []}}
        
    @api.onchange('commune_id')
    def _onchange_commune_id(self):
        if self.commune_id:
            return {'domain': {'fkt': [('id', 'in', self.commune_id.x_studio_fokontany.ids)]}}
        else:
            return {'domain': {'fkt': []}}

