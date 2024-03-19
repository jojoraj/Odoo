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
from datetime import datetime, timedelta

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning


class Lead(models.Model):
    _inherit = 'crm.lead'
    _order = "pick_up_datetime, id desc"

    pick_up_datetime = fields.Datetime("Pick up date and time")
    # TO DO: Geotab
    pick_up_zone = fields.Text("Exact location pick up")
    pick_up_zone_id = fields.Many2one("res.district", 'Pick up zone')
    pick_up_lat = fields.Char('Latitude of pick up zone')
    pick_up_long = fields.Char('Longitude of pick up zone')
    # TO DO: Geotab
    destination_zone = fields.Text("Exact location destination")
    destination_zone_id = fields.Many2one("res.district", 'Destination Zone')
    dest_lat = fields.Char('Latitude of destination')
    dest_long = fields.Char('Longitude of destination')
    duration = fields.Float()
    estimated_kilometers = fields.Float()
    client_note = fields.Text("Client notes")
    refusal_ids = fields.Many2many('crm.refusal', string='Reason for refusal')
    refusal_remark = fields.Text()
    planning_id = fields.Many2one('planning.slot', string="Planning")
    hour = fields.Char('Pick up Hour', compute='_compute_hour', store=True)
    assignment_reminder = fields.Selection(
        [('none', 'None'), ('to_do', 'To do'), ('processed_today', 'To be processed today'),
         ('late', 'Late')], string='Type', readonly=True, compute='_compute_reminder', store=False)
    payment_method_note = fields.Char()
    reference_code = fields.Char()

    @api.model
    def action_mark_as_accounted(self):
        active_ids = self._context.get('active_ids')
        lead_ids = self.browse(active_ids)
        for lead_id in lead_ids:
            lead_id.stage_id = self.env.ref('crm.stage_lead4').id
        return True

    @api.depends('pick_up_datetime')
    def _compute_hour(self):
        for rec in self:
            rec.hour = fields.Datetime.context_timestamp(self, rec.pick_up_datetime).strftime(
                "%H:%M") if rec.pick_up_datetime else False

    @api.depends('name', 'pick_up_datetime', 'stage_id')
    def _compute_reminder(self):
        tz = self.env.user.tz or 'UTC'
        utc_now = pytz.utc.localize(datetime.utcnow())
        tz_now = utc_now.astimezone(pytz.timezone(tz))
        late_now = tz_now + timedelta(hours=1)
        for rec in self:
            new_ride = self.env.ref('crm.stage_lead1').id
            if rec.stage_id.id == new_ride and rec.pick_up_datetime:
                tz_pick_up_datetime = fields.Datetime.from_string(rec.pick_up_datetime)
                pick_up_datetime = tz_pick_up_datetime.astimezone(pytz.timezone(tz))
                if pick_up_datetime < late_now:
                    rec.assignment_reminder = 'late'
                elif pick_up_datetime > late_now and pick_up_datetime.date() == late_now.date():
                    rec.assignment_reminder = 'processed_today'
                else:
                    rec.assignment_reminder = 'to_do'
            else:
                rec.assignment_reminder = 'none'

    def write(self, values):
        for rec in self:
            if values.get('stage_id') == self.env.ref('esanandro_crm.stage_lead5').id:
                if not values.get('refusal_ids', rec.refusal_ids) or not values.get('refusal_remark', rec.refusal_remark):
                    action_error = {
                        'view_mode': 'form',
                        'name': _('Define reason for refusal'),
                        'type': 'ir.actions.act_window',
                        # 'view_type': 'form',
                        'res_model': 'crm.refusal.wizard',
                        'views': [[False, 'form']],
                        'target': 'new',
                        'context': {
                            'default_crm_id': rec.id,
                            'default_refusal_ids': values.get('refusal_ids', rec.refusal_ids).ids if values.get(
                                'refusal_ids', rec.refusal_ids).ids else False,
                            'default_refusal_remark': values.get('refusal_remark', rec.refusal_remark),
                        }
                    }

                    error_msg = _(
                        'You must define the refusal reason and refusal remark fields, to do this click on the refuse button.')
                    raise RedirectWarning(error_msg, action_error, _('Refuse'))
            new_ride = self.env.ref('crm.stage_lead1')
            activity_id = self.env['mail.activity'].search(
                [('res_model', '=', 'crm.lead'), ('res_id', '=', rec.id)])
            if (rec.stage_id == new_ride if rec.stage_id else False) and ((values.get('stage_id') != new_ride.id) if values.get('stage_id') else False):
                if activity_id:
                    activity_id.unlink()
            if (values.get('pick_up_datetime', rec.pick_up_datetime) and values.get('stage_id',
                                                                                    rec.stage_id.id) == new_ride.id):
                if not activity_id:
                    self.env['mail.activity'].create({
                        'res_id': rec.id,
                        'res_model': 'crm.lead',
                        'res_model_id': self.env['ir.model']._get('crm.lead').id,
                        'user_id': 2,
                        'date_deadline': values.get('pick_up_datetime', rec.pick_up_datetime).date() if type(
                            values.get('pick_up_datetime', rec.pick_up_datetime)) is datetime else datetime.strptime(
                            values.get('pick_up_datetime', rec.pick_up_datetime),
                            '%Y-%m-%d %H:%M:%S').date(),
                        'datetime_deadline': values.get('pick_up_datetime', rec.pick_up_datetime) if type(
                            values.get('pick_up_datetime', rec.pick_up_datetime)) is datetime else datetime.strptime(
                            values.get('pick_up_datetime', rec.pick_up_datetime),
                            '%Y-%m-%d %H:%M:%S'),
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id
                    })
                else:
                    activity_id.write({
                        'date_deadline': values.get('pick_up_datetime', rec.pick_up_datetime).date() if type(
                            values.get('pick_up_datetime', rec.pick_up_datetime)) is datetime else datetime.strptime(
                            values.get('pick_up_datetime', rec.pick_up_datetime),
                            '%Y-%m-%d %H:%M:%S').date(),
                        'datetime_deadline': values.get('pick_up_datetime', rec.pick_up_datetime) if type(
                            values.get('pick_up_datetime', rec.pick_up_datetime)) is datetime else datetime.strptime(
                            values.get('pick_up_datetime', rec.pick_up_datetime),
                            '%Y-%m-%d %H:%M:%S'),
                    })
        return super(Lead, self).write(values)

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        # self.flush()
        if res.env.context.get('create_from', '') == 'planning.slot':
            planning = self.env['planning.slot'].browse(vals.get('planning_id'))
            pick_up_zone_id = self.env['res.district'].browse(vals.get('pick_up_zone_id'))
            destination_zone_id = self.env['res.district'].browse(vals.get('destination_zone_id'))
            note = ''
            if vals.get('client_note', False):
                note = '\n %s' % (vals.get('client_note', ''))
            order_line = [(0, 0, {
                'name': planning.product_id.name,
                'product_id': planning.product_id.id,
                'product_uom': planning.product_id.uom_po_id.id,
                'product_uom_qty': vals.get('estimated_kilometers'),
                'price_unit': planning.product_id.list_price,
            }), (0, 0, {
                'display_type': 'line_note',
                'name': _('Pick up zone: %s (%s) - Destination zone: %s (%s) [%s] %s') % (
                    pick_up_zone_id.name or '', vals.get('pick_up_zone'), destination_zone_id.name or '',
                    vals.get('destination_zone'),
                    vals.get('pick_up_datetime'), note),
            })]

            order_id = self.env['sale.order'].create({
                'role_id': vals.get('role_id'),
                'pick_up_datetime': vals.get('pick_up_datetime'),
                # 'date_deadline': vals.get('end_datetime'),
                # 'estimated_kilometers': vals.get('estimated_kilometers'),
                'client_note': vals.get('client_note'),
                'pick_up_zone_id': vals.get('pick_up_zone_id'),
                'destination_zone_id': vals.get('destination_zone_id'),
                'pick_up_zone': vals.get('pick_up_zone'),
                'destination_zone': vals.get('destination_zone'),
                'duration': vals.get('duration'),
                'partner_id': vals.get('partner_id'),
                'opportunity_id': res.id,
                'origin': res.name,
                'order_line': order_line,
                'payment_method_note': vals.get('payment_method_note', '')
            })
            planning.sale_line_id = order_id.order_line[0]
        if vals.get('pick_up_datetime', False):
            self.env['mail.activity'].create({
                'res_id': res.id,
                'res_model': 'crm.lead',
                'res_model_id': self.env['ir.model']._get('crm.lead').id,
                'user_id': 2,
                'date_deadline': vals.get('pick_up_datetime').date() if type(
                    vals.get('pick_up_datetime')) is datetime else datetime.strptime(vals.get('pick_up_datetime'),
                                                                                     '%Y-%m-%d %H:%M:%S').date(),
                'datetime_deadline': vals.get('pick_up_datetime') if type(
                    vals.get('pick_up_datetime')) is datetime else datetime.strptime(
                    vals.get('pick_up_datetime'),
                    '%Y-%m-%d %H:%M:%S'),
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id
            })
        return res
