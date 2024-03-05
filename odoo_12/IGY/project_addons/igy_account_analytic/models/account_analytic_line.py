# -*- coding: utf-8 -*-

from odoo import models,api,fields,exceptions

class AccountAnalytic(models.Model):
    _inherit="account.analytic.line"


    @api.constrains('date')
    def _check_date_is_after_today(self):
        if self.date > fields.date.today() and self.project_id.name != 'INGENOSYA_CONGES':
            raise exceptions.ValidationError("Votre feuille de temps ne doit pas dépasser la date d'aujourd'hui")
