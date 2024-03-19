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

from odoo import fields, models


class ResCity(models.Model):
    _name = 'res.city'
    _order = 'name'

    name = fields.Char()
    code = fields.Char()
    state_ids = fields.One2many("res.country.state", 'city_id', string='States')


class CountryState(models.Model):
    _inherit = 'res.country.state'

    city_id = fields.Many2one("res.city", string='City')
    district_ids = fields.One2many("res.district", 'state_id', string='Districts')


class ResDistrict(models.Model):
    _name = 'res.district'
    _order = 'name'

    name = fields.Char()
    code = fields.Char()
    state_id = fields.Many2one("res.country.state", string='Commune')

    def name_get(self):
        self = self.sudo()
        result = []
        for rec in self:
            if not rec.state_id:
                res = [u'%s \U0001F4AC' % rec.name]
            else:
                res = [rec.id, "%s - %s" % (rec.name, rec.state_id.name)]
            result.append(res)
        return result
