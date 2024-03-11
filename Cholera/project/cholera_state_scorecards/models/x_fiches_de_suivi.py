# -*- coding: utf-8 -*-

from odoo import _, models, fields,api
from odoo.exceptions import UserError


class X_fiches_de_suivi(models.Model):
    _inherit = 'x_fiches_de_suivi'
    
    x_has_cholera = fields.Boolean(
        related= 'x_studio_nom_de_la_personne.has_Cholera',
        store=True
        )