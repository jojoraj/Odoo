##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from random import randint

from odoo import fields, models


class Refusal(models.Model):
    _name = 'crm.refusal'
    _description = "CRM Refusal"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Refusal Name', required=True, translate=True)
    color = fields.Integer(default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Refusal name already exists !"),
    ]
