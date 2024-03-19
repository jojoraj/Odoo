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
from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    iban_code = fields.Char('IBAN', compute='_compute_iban')

    @api.depends('acc_number', 'bank_id')
    def _compute_iban(self):
        for rec in self:
            if rec.acc_number and rec.bank_id and rec.bank_id.country.code and rec.bank_id.code:
                values = rec.bank_id.country.code + rec.bank_id.code + rec.acc_number
                rec.iban_code = values.replace(" ", "")
            else:
                rec.iban_code = ""
