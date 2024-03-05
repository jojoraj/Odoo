# -*- coding: utf-8 -*-

import datetime
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class HrCheckInformation(models.Model):
    _name = "hr.check.information"

    name = fields.Many2one('hr.information.theme', string=_("Thème"))
    date = fields.Date(string=_("Date"), default=fields.Date.today())
    responsable_id = fields.Many2one('res.users', string=_("Responsable"))
    emagement = fields.Boolean(string=_("Emargement"))
    employee_id = fields.Many2one('hr.employee', string=_("Employé"))

    @api.constrains('employee_id', 'name')
    def verify_check_in_exist(self):
        for line in self:
            check_results = self.search(
                [('employee_id', '=', line.employee_id.id), ('name', '=', line.name.id), ('id', '!=', line.id)]).mapped(
                'id')
            if len(check_results) > 0:
                raise UserError(_(
                    """
                    {0} existe déjà parmi les check-in d'intégration de l'employé {1}
                    """.format(
                        line.name.name,
                        line.employee_id.name
                    )))


class HrInformationTheme(models.Model):
    _name = "hr.information.theme"

    name = fields.Char(string=_("Thème"))
