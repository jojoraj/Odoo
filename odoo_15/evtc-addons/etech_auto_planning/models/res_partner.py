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

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean("Is driver")
    is_b2b = fields.Boolean(string="Is client B2B")
    related_company = fields.Many2one('res.partner', string='Related Company', index=True)


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(['|', ('phone', operator, name), ('mobile', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = []
        for rec in self:
            rec_name = rec.name
            if self.env.context.get('show_phone', False):
                if rec.phone and rec.phone != '0':
                    rec_name = "%s (%s)" % (rec.name, rec.phone)
                    result.append((rec.id, rec_name))
                elif rec.mobile and rec.mobile != '0':
                    rec_name = "%s (%s)" % (rec.name, rec.mobile)
                    result.append((rec.id, rec_name))
                else:
                    result.append((rec.id, rec_name))
            else:
                rec_name = rec._get_name()
                result.append((rec.id, rec_name))
        return result
