# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    domaine = fields.Char(string="Domaine d'activités")
    snov = fields.Char(string="Domaine snov")
    personne = fields.Char(string="Nombre de personne dans la societé")
    ca = fields.Char(string="CA de la societé")
    cc = fields.Char(string="code communale de la societé")
    address_type = fields.Selection(
        selection=[('personnel','Personnel'),
                   ('professionnel','Professionnel'),
                   ('generique','Generique')],
        string="Type d'adresse",
        default='personnel'
    )
    last_address = fields.Char(
        string="Ancienne adresse"
    )
    updated_address = fields.Char(
        string="MAJ adresse"
    )
    activity_info = fields.Char(
        string="Liste info activité"
    )
    company_type = fields.Selection(
        string='Company Type',
        selection=[('person', 'Individual'),
                   ('company', 'Company')],
        compute='_compute_company_type',
        inverse='_write_company_type',
        store=True
    )
    client_title = fields.Selection(
        selection=[('Mr','Monsieur'),
                   ('Mme','Madame')],
        string="Titre",
        default='Mr'
    )
    activity = fields.Selection(
        selection=[('1','Développeur'),
                   ('2','Editeur'),
                   ('3','Installation matérielle'),
                   ('4','Intégrateur'),
                   ('5','Formation'),
                   ('6','Assistance'),
                   ('7','Agence Web')],
        string="Activités",
    )
    res_activity_ids = fields.Many2many(
        comodel_name='res.partner.activity',
        relation='res_partner_activity_rel',
        column1='partner_id',
        column2='activity_id',
        string="Activités",
    )
    activity_id = fields.Many2one(
        comodel_name='res.partner.activity',
        string="Activités Many2one"
    )
    linkedin_link = fields.Char(
        string="Lien linkedin"
    )
    firstname = fields.Char(
        string="Prenoms"
    )
    is_ex_candidat = fields.Boolean(string=_("Est un ex candidat"))

    @api.multi
    def update_address(self, vals):
        addr_vals = {key: vals[key] for key in self._address_fields() if key in vals and len(self._address_fields()) > 0}
        if addr_vals:
            return super(ResPartnerInherit, self).write(addr_vals)

class ResPartnerActivity(models.Model):
    _name = 'res.partner.activity'
    _description = 'Activités du client'

    name = fields.Char(
        string="Nom"
    )
    color = fields.Integer(
        string="Color"
    )
    partner_id = fields.Many2one(
        string="Client"
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner.activity',
        relation='activity_res_partner_rel',
        column1='activity_id',
        column2='partner_id',
        string="Clients",
    )