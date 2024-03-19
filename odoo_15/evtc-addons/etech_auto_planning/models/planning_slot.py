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

import datetime

from odoo import _, api, fields, models
from odoo.osv.expression import AND


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    partner_id = fields.Many2one('res.partner', 'Customer', compute='_compute_partner_id', readonly=False, store=True)
    phone = fields.Char(compute='_compute_phone')
    # TO DO: Geotab
    pick_up_zone = fields.Text("Exact location pick up")
    pick_up_zone_id = fields.Many2one("res.district", 'Pick up zone')
    # TO DO: Geotab
    destination_zone = fields.Text("Exact location destination")
    destination_zone_id = fields.Many2one("res.district", 'Destination Zone')
    estimated_kilometers = fields.Float()
    client_note = fields.Text("Client notes")
    role_id = fields.Many2one('planning.role', string="Role")
    product_id = fields.Many2one('product.product', string="Product", compute='_compute_partner_id', readonly=False,
                                 store=True)

    crm_lead_id = fields.Many2one('crm.lead', string="Leads")
    hour = fields.Char('Pick up Hour', compute='_compute_hour', store=True)

    @api.depends('start_datetime')
    def _compute_hour(self):
        for rec in self:
            rec.hour = fields.Datetime.context_timestamp(self, rec.start_datetime).strftime(
                "%H:%M") if rec.start_datetime else False

    @api.model
    def get_order_ids(self, role_id, searchDomain, limit, offset):
        self.clear_caches()
        # TODO: Uncomment these lines to filter slot by date
        # before = int(
        #     self.env['ir.config_parameter'].sudo().get_param('etech_auto_planning.default_slot_before_value', 4))
        # after = int(
        #     self.env['ir.config_parameter'].sudo().get_param('etech_auto_planning.default_slot_after_value', 12))
        # order_ids = self.sudo().search([('role_id', '=', role_id)]).mapped(
        #     'sale_line_id.order_id').filtered(lambda x: x.pick_up_datetime and fields.Datetime.now() + relativedelta(
        #     hours=-before) <= x.pick_up_datetime <= fields.Datetime.now() + relativedelta(
        #     hours=+after) and 'done' not in x.mapped('pos_order_line_ids.order_id.state'))
        order_ids = self.sudo().search([('role_id', '=', role_id)]).mapped(
            'sale_line_id.order_id').filtered(lambda x: not x.pos_order_line_ids)
        stage_domain = [
            self.env.ref('crm.stage_lead1').id,
            self.env.ref('crm.stage_lead4').id,
            self.env.ref('esanandro_crm.stage_lead5').id
        ]
        domain = [('id','in',order_ids.ids),'|', ('opportunity_id', '!=', False),
                ('opportunity_id.stage_id', 'not in',stage_domain),
            ]
        if searchDomain:
            domain = AND([domain, searchDomain])
        orders = self.env['sale.order'].sudo()
        values = orders.search_read(domain, ['id', 'name', 'partner_id', 'amount_total', 'pick_up_datetime',
                                             'state', 'user_id'], order='pick_up_datetime',
                                    offset=offset, limit=limit)
        values_count = orders.search_count(domain)
        for val in values:
            if val['partner_id']:
                partner_id = self.env['res.partner'].search([('id', '=', val['partner_id'][0])])
                if partner_id:
                    val['phone'] = partner_id.phone if partner_id.phone else partner_id.mobile
        return dict(orders=values, ordersCount=values_count)

    @api.depends('partner_id')
    def _compute_phone(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.phone:
                rec.phone = rec.partner_id.phone
            elif rec.partner_id and rec.partner_id.mobile:
                rec.phone = rec.partner_id.mobile
            else:
                rec.phone = False

    @api.depends('sale_line_id')
    def _compute_partner_id(self):
        for rec in self:
            rec.partner_id = rec.sale_line_id.order_id.partner_id.id if rec.sale_line_id else False
            rec.product_id = rec.sale_line_id.product_id.id if rec.sale_line_id else False

    def write(self, values):
        res = super(PlanningSlot, self).write(values)
        self.flush()
        # if res.env.context.get('write_from', False)
        if self.sale_line_id and self.sale_line_id.order_id.role_id:
            self.sale_line_id.order_id.role_id = self.role_id.id
            self.sale_line_id.order_id.opportunity_id.role_id = self.role_id.id \
                if self.sale_line_id.order_id.opportunity_id else False
        if self.sale_line_id and self.product_id and self.partner_id:
            order = {}
            order_line = {}
            lead = {}
            values_need = dict()
            values_need.update(values)
            key_to_keep = ['role_id', 'partner_id', 'pick_up_zone_id', 'pick_up_zone', 'destination_zone_id',
                           'destination_zone', 'start_datetime', 'duration', 'client_note', 'estimated_kilometers']
            for key, _value in values.items():
                if key not in key_to_keep:
                    del values_need[key]
            if 'start_datetime' in values_need:
                del values_need['start_datetime']
                values_need['pick_up_datetime'] = self.start_datetime
            if 'product_id' in values_need:
                order_line['product_id'] = self.product_id
                del values_need['product_id']
            # Update duration in order and lead
            values_need['duration'] = self.duration
            lead = values_need
            if 'estimated_kilometers' in values_need:
                order_line['product_uom_qty'] = self.estimated_kilometers
                del values_need['estimated_kilometers']
            order = values_need
            self.sale_line_id.order_id.write(order)
            self.sale_line_id.write(order_line)
            self.sale_line_id.order_id.opportunity_id.write(lead)
        return res

    def name_get(self):
        group_by = self.env.context.get('group_by', [])
        field_list = [fname for fname in self._name_get_fields() if fname not in group_by]

        # Sudo as a planning manager is not able to read private project if he is not project manager.
        self = self.sudo()
        result = []
        for slot in self:
            # label part, depending on context `groupby`
            name_values = [self._fields[fname].convert_to_display_name(slot[fname], slot) for fname in field_list if
                           slot[fname]][:3]  # limit to 3 labels
            name = ' - '.join(name_values) or slot.resource_id.name

            # add unicode bubble to tell there is a note
            if slot.name:
                name = u'%s \U0001F4AC' % name
            if slot.sale_line_id:
                result.append([slot.id, "%s (%s)" % (slot.partner_id.name, slot.sale_line_id.order_id.name)])
            else:
                result.append([slot.id, name or ''])
        return result

    @api.model
    def create(self, vals):
        res = super(PlanningSlot, self).create(vals)
        if not res.env.context.get('create_from', False) and \
                not vals.get('sale_line_id') and vals.get('partner_id', False) and vals.get('product_id', False):
            delta = datetime.datetime.strptime(vals.get('end_datetime'),
                                               '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                vals.get('start_datetime'), '%Y-%m-%d %H:%M:%S')
            sec = delta.seconds
            hours = sec / 3600
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            crm_lead_id = self.env['crm.lead'].with_context(create_from="planning.slot").create({
                'name': _("Opportunity %s") % partner_id.name,
                'role_id': vals.get('role_id'),
                'pick_up_datetime': vals.get('start_datetime'),
                # 'date_deadline': vals.get('end_datetime'),
                'estimated_kilometers': vals.get('estimated_kilometers'),
                'client_note': vals.get('client_note'),
                'pick_up_zone_id': vals.get('pick_up_zone_id'),
                'destination_zone_id': vals.get('destination_zone_id'),
                'pick_up_zone': vals.get('pick_up_zone'),
                'destination_zone': vals.get('destination_zone'),
                'duration': hours,
                'stage_id': self.env.ref('crm.stage_lead2').id,
                'type': 'opportunity',
                'partner_id': vals.get('partner_id'),
                'planning_id': res.id,
            })
            self.crm_lead_id = crm_lead_id.id
        return res
