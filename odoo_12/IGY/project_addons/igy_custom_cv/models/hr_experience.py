# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrExperience(models.Model):
    _name = 'hr.experience'
    _description = 'Experience'
    
    period = fields.Char('Période', required=True)
    post = fields.Char('Poste occupé', required=True)
    project = fields.Char('Projet')
    company = fields.Char('Société', required=True)
    description = fields.Html('Description du projet', default=lambda self: self.get_default_html())
    link = fields.Many2one('hr.employee', string='Nom', readonly=True)

    def get_default_html(self):
        default_html = """
            <p>
                <span style="font-weight: bold; font-size: 12pt;">Nom du client</span>:
                <span style="font-style: initial">Description brève du projet(2 lignes maximum)</span>
            </p>
            <p>
                <ul  style="font-size: 14px; font-family: 'Lucida Grande', Helvetica, Verdana, Arial, sans-serif;">
                    <li style="margin-bottom: 10px;">Tache 1</li>
                    <li style="margin-bottom: 10px;">Tache 2</li>
                    <li style="margin-bottom: 10px;">Tache 3</li>
                </ul>
            </p>
            <p>
                <span class='text-muted' style="font-family: "Lucida Grande", Helvetica, Verdana, Arial, sans-serif; font-size: 13px;">
                    Environnement technique:
                </span>
            </p>
        """
        return default_html





    
    