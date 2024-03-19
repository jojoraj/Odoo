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
import logging
from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning, ValidationError
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    role_id = fields.Many2one('planning.role', string="Role")
    state_value = fields.Char(compute='_compute_state_value')

    @api.depends('stage_id')
    def _compute_state_value(self):
        for rec in self:
            rec.state_value = rec.stage_id.export_data(['id']).get('datas', [])[0][0]

    def action_cancel_stage(self):
        self.write({
            'stage_id': self.env.ref('esanandro_crm.stage_lead5').id
        })

    def confirm_stage_without_return(self):
        self.with_context(from_auto_planning=True).write({
            'stage_id': self.env.ref('esanandro_crm.stage_lead7').id
        })
 
    def action_confirm_stage(self):
        self.confirm_stage_without_return()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'context': self._context,
        }

    def write(self, values):
        if values.get('stage_id', False) and not values.get('stage_id',False) ==  self.env.ref('crm.stage_lead1').id and not values.get(
                'role_id', self.role_id) and not self.env.context.get('from_auto_planning'):
            not_confirmed = [self.env.ref('esanandro_crm.stage_lead5').id , self.env.ref('esanandro_crm.stage_lead7').id]
            if values.get('stage_id') not in  not_confirmed:
                action_error = {
                    'view_mode': 'form',
                    'name': _('Assignment'),
                    'res_model': 'auto.planning.wizard',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'views': [[False, 'form']],
                    'context': {
                        'active_ids': self._ids
                    }
                }
                error_msg = _('You cannot change the recording status without making the vehicle assignment') 
                raise RedirectWarning(error_msg, action_error, _('Assignment'))
        if values.get('stage_id', False) == self.env.ref('esanandro_crm.stage_lead5').id:
            if values.get('refusal_ids', self.refusal_ids) or not values.get('refusal_remark', self.refusal_remark):
                for order in self.order_ids.filtered(lambda o: o.state == 'draft'):
                    order.unlink()

        if values.get('stage_id') == self.env.ref('esanandro_crm.stage_lead7').id:
            order_id = self.convert_lead_to_quotation()
            self.create_planification_crm(order_id)
            self.send_notification_crm()
        return super(CrmLead, self).write(values)


    def convert_lead_to_quotation(self):
        """
            CONVERT CRM TO QUOTATION 
            :rtype: object
        """
        for record_id in self:
            partner_id = self.env['res.partner'].search([('email_normalized', '=', record_id.email_from),
                                                      ('id', '=', record_id.partner_id.id)],
                                                    limit=1) if record_id.email_from else False

            if not partner_id:
                record_id._handle_partner_assignment(create_missing=True)
                partner_id = record_id.partner_id
            else:
                record_id._handle_partner_assignment(force_partner_id=partner_id.id, create_missing=False)
         
            list_price = record_id.model_category_id.list_price
            pickup_date = record_id.pick_up_datetime.date()
            day = pickup_date.strftime("%w")
            day_spring = (int(day) - 1) % 7
            hours = record_id.pick_up_datetime.time().hour
            minutes = record_id.pick_up_datetime.time().minute
            float_hours = hours + (minutes / 100)
            product_ids = []
            kilometer = record_id.estimated_kilometers
            note = '\n %s' % record_id.client_note if record_id.client_note else ''
            if record_id.is_location:
                berline_found = list_price.filtered(
                    lambda y: y.is_location and y.vehicle_location_id.id == record_id.location_duration.id
                            and y.resource_calendar_id.attendance_ids.filtered(
                        lambda z: z.dayofweek == str(day_spring) and z.hour_from <= float_hours < z.hour_to))
                kilometer = 1
            else:
                berline_found = list_price.filtered(
                    lambda y: not y.is_location and y.resource_calendar_id.attendance_ids.filtered(
                        lambda z: z.dayofweek == str(day_spring) and z.hour_from <= float_hours < z.hour_to))
                if record_id.as_many_course:
                    kilometer_many_course = record_id.others_destination.mapped('kilometers_estimted')
                    if kilometer_many_course:
                        kilometer = sum(kilometer_many_course)
                    

            if berline_found:
                section_note_wait = ''
                price_wait_time = 0
                berline_found = berline_found[0 % len(berline_found)]
                product_id = berline_found.product_id
                product_ids += [product_id.id]
                if record_id.as_many_course:
                    is_wait = record_id.others_destination.filtered(lambda o: o.delay)
                    if is_wait:
                        product_ids += [berline_found.product_wait_id.id]
                        try:
                            xtime = 0
                            for x in record_id.others_destination.wait_time:
                                xtime += x.wait_time_mn
                            h, m = str(xtime // 60), str(xtime % 60)
                            h = len(h) > 1 and h or '0' + h
                            m = len(m) > 1 and m or '0' + m
               
                            price_wait_time =  0
                        except Exception as errors:
                            _logger.error(errors)
                            h, m = '', ''
                        finally:
                            section_note_wait = f"Temps d'attente estimatif {h}:{m}"
                elif not record_id.is_location:
                    product_ids += [berline_found.product_wait_id.id]
                order_line = []
                for product in self.env['product.product'].browse(product_ids).exists():
                    if record_id.is_location:
                        price_units = record_id.location_duration.price
                    else:
                        price_units = product.time_wait_ok and price_wait_time or product.list_price

                    my_kilometers = product.time_wait_ok and 1 or kilometer

                    if product.time_wait_ok:
                        line_notes = section_note_wait
                    else:
                        line_notes = ''


                    order_line += [
                        (0, 0, {
                            'name': product.name,
                            'product_id': product.id,
                            'product_uom_qty': my_kilometers,
                            'product_uom': product.uom_po_id.id,
                            'price_unit': price_units,
                        })
                    ]
                    if line_notes:
                        order_line += [
                            (0, 0, {
                                'display_type': 'line_note',
                                'name': line_notes
                            })
                        ]
            else:
                raise ValidationError(_('no working vehicle on this day'))
            

            if record_id.order_ids:
                order_id = record_id.order_ids[-1]
                order_id.order_line = False
                order_id.update({
                    'order_line': order_line
                })
                return order_id
            else:
                order_id = self.env['sale.order'].create({
                    'partner_id': partner_id.id,
                    'opportunity_id': record_id.id,
                    'campaign_id': record_id.campaign_id.id,
                    'medium_id': record_id.medium_id.id,
                    'origin': record_id.name,
                    'source_id': record_id.source_id.id,
                    'pick_up_datetime': record_id.pick_up_datetime,
                    'pick_up_zone_id': record_id.pick_up_zone_id.id,
                    'destination_zone_id': record_id.destination_zone_id.id,
                    'pick_up_zone': record_id.pick_up_zone,
                    'destination_zone': record_id.destination_zone,
                    'duration': record_id.duration,
                    'estimated_kilometers': record_id.estimated_kilometers,
                    'client_note': record_id.client_note,
                    'company_id': record_id.company_id.id or self.env.company.id,
                    'tag_ids': [(6, 0, record_id.tag_ids.ids)],
                    'order_line': order_line,
                    'reference_code': record_id.reference_code
                })
                return order_id

    def create_planification_crm(self, order_id):
        """
            CREATION PLANIFICATION
            FROM CRM LEAD, role should update manually
        """
        for record_id in self:
            # check slot if exist :
            planning_slot_id = self.env['planning.slot'].search([('crm_lead_id','=',record_id.id)])
            
            if planning_slot_id:
                single_planning_slot_id = planning_slot_id[0]
                single_planning_slot_id.sudo().write({
                    'start_datetime': record_id.pick_up_datetime,
                    'end_datetime': record_id.pick_up_datetime + relativedelta(hours=+record_id.duration),
                    'allocated_hours': record_id.duration,
                    'pick_up_zone_id': record_id.pick_up_zone_id.id,
                    'destination_zone_id': record_id.destination_zone_id.id,
                    'pick_up_zone': record_id.pick_up_zone,
                    'destination_zone': record_id.destination_zone,
                    'estimated_kilometers': record_id.estimated_kilometers,
                    'client_note': record_id.client_note,
                    'partner_id': record_id.partner_id.id,
                    'crm_lead_id': record_id.id,
                    'sale_line_id': order_id.order_line[0].id
                })
                return single_planning_slot_id.id
            else:
                val = self.env['planning.slot'].sudo().with_context(create_from="crm.lead").create({
                    'start_datetime': record_id.pick_up_datetime,
                    'end_datetime': record_id.pick_up_datetime + relativedelta(hours=+record_id.duration),
                    'allocated_hours': record_id.duration,
                    'pick_up_zone_id': record_id.pick_up_zone_id.id,
                    'destination_zone_id': record_id.destination_zone_id.id,
                    'pick_up_zone': record_id.pick_up_zone,
                    'destination_zone': record_id.destination_zone,
                    'estimated_kilometers': record_id.estimated_kilometers,
                    'client_note': record_id.client_note,
                    'partner_id': record_id.partner_id.id,
                    'crm_lead_id': record_id.id,
                    'sale_line_id': order_id.order_line[0].id
                })
                return val.id

    def send_notification_crm(self):
        partner_id = self.partner_id
        user_id = self.partner_id.user_ids[0] if self.partner_id.user_ids else self.env['res.users']
        if partner_id and partner_id.country_id.code == 'MG':
            sms_id = self.env.ref('esanandro_crm.sms_crm_lead7_notif')
            string = sms_id._render_field('body', [self.id], set_lang=sms_id.lang)[self.id]
            user_id.send_orange_sms(body=string, force_send=True, senders=partner_id)
        else:
            try:
                template_mail = self.env.ref(
                    'esanandro_crm.email_template_data_crm_lead_validation_notification',
                    raise_if_not_found=False)
                template_mail.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.info(f"{'=' * 25} Mail has been not send with reason: {str(e)} {'=' * 25}")