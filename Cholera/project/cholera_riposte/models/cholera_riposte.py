# -*- coding: utf-8 -*-

from odoo import models, fields, _


class CholeraRiposte(models.Model):
    _name = 'cholera.riposte'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string="Patient", required=True)
    is_chemoprophylaxis = fields.Boolean(string='Chimioprophylaxie')
    chemoprophylaxis_number = fields.Integer(string='Nombre de Chimioprophylaxie')
    Number_of_input = fields.Integer(string="Nombre d'intrant")
    date_of_repost = fields.Date(string='Date de riposte', required=True)
    province = fields.Many2one(comodel_name="res.province", related="partner_id.province_id")
    region = fields.Many2one(string='Région', comodel_name='res.region', related="partner_id.region_id")
    district = fields.Many2one(string='District', comodel_name='res.district', related="partner_id.district_id")
    town = fields.Many2one(string='Commune', comodel_name='res.commune', related="partner_id.commune_id")
    village = fields.Many2one(string='Fokontany', related='partner_id.x_studio_field_tU4nQ')
    sanitary = fields.Many2one('res.province', string="SANITAIRE")
