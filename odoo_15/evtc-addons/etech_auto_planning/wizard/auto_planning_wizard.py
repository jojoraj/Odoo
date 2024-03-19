##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 Arkeup (<https://www.etechconsulting-mg.com>). All Rights Reserved
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
import time
from collections import OrderedDict

import phonenumbers
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, ValidationError

# Get server timezone
TZ = (time.timezone / 60 / 60) if time.timezone != 0 else -3
MARGIN = 3600
_logger = logging.Logger(__name__)


def format_phone_number(phone_number, country):
    try:
        phone_number = str(phonenumbers.parse(phone_number).national_number)
    except Exception as e:
        _logger.info('phone_number not formatted : {}'.format(e))

    return phone_validation.phone_format(
        phone_number,
        country.code if country else None,
        country.phone_code if country else None,
        force_format='INTERNATIONAL',
        raise_exception=True
    )


class AutoPlanningWizard(models.TransientModel):
    _name = 'auto.planning.wizard'
    _description = 'Auto Planning'

    @api.model
    def default_get(self, fields):
        planning = super(AutoPlanningWizard, self).default_get(fields)
        record_id = self.env['crm.lead'].sudo().browse(self._context.get('active_ids'))
        x = record_id.pick_up_datetime
        y = record_id.pick_up_datetime + relativedelta(hours=+record_id.duration)
        midnight = y + relativedelta(days=+1, hours=TZ, hour=0, minute=0, second=0, seconds=-1)
        if not record_id.pick_up_datetime:
            raise UserError(_("Please set pick up date before continuing"))
        role_ids = self.env['planning.slot'].sudo().search([('role_id.active', '=', True)]).mapped('role_id')
        # planning already existe in period of current record
        slot_ids = self.env['planning.slot'].sudo().search(
            [('role_id.active', '=', True),
             ('end_datetime', '>', x + relativedelta(hour=0, minute=0, second=0)),
             ('end_datetime', '<', x + relativedelta(days=+1, hour=0, minute=0, second=0))])
        result = {}
        for slot_id in slot_ids.sorted(lambda x: x.start_datetime):
            if slot_id.role_id.id not in result:
                result[slot_id.role_id.id] = [{'start_datetime': slot_id.start_datetime,
                                               'end_datetime': slot_id.end_datetime, 'slot_id': slot_id.id}]
            else:
                result[slot_id.role_id.id] += [{'start_datetime': slot_id.start_datetime,
                                                'end_datetime': slot_id.end_datetime, 'slot_id': slot_id.id}]
        update_values = {}
        to_remove = []
        for n in result:
            index = -1
            is_after = False
            is_partial = False
            for res in result[n]:
                slot_id = self.env['planning.slot'].sudo().browse([res['slot_id']])
                index += 1
                # Break if pick up date start and end is inside the current slot
                if res['start_datetime'] <= x <= res['end_datetime'] and res['start_datetime'] <= y <= res[
                    'end_datetime']:
                    if n in update_values:
                        # Update end_datetime if booking is before the current slot
                        update_values[n]['end_datetime'] = res['start_datetime']
                        update_values[n]['state'] = 'is_assigned'
                    to_remove.append(slot_id.role_id.id)
                    break
                if x > res['start_datetime']:
                    if x >= res['end_datetime']:
                        # Available slot
                        is_after = True
                        update_values[n] = self.with_context(result=result,
                                                             is_after=is_after
                                                             ).update_values(slot_id, res['end_datetime'], midnight,
                                                                             'available')
                    else:
                        # Partial slot
                        is_after = True
                        is_partial = True
                        update_values[n] = self.with_context(result=result,
                                                             is_after=is_after,
                                                             is_partial=is_partial
                                                             ).update_values(slot_id, res['end_datetime'], midnight,
                                                                             'is_assigned')
                else:
                    start_time = x + relativedelta(hours=TZ, hour=0, minute=0, second=0)
                    if y > res['start_datetime']:
                        # Partial slot
                        is_partial = True
                        if n in update_values:
                            # Update end_datetime if booking is before the current slot
                            update_values[n]['end_datetime'] = res['start_datetime']
                            update_values[n]['state'] = 'is_assigned'
                            break
                        else:
                            update_values[n] = self.with_context(result=result, is_after=is_after).update_values(
                                slot_id,
                                start_time,
                                res['start_datetime'],
                                'is_assigned')
                    else:
                        # Available slot
                        if n in update_values:
                            # Update end_datetime if booking is before the current slot
                            if is_after:
                                update_values[n]['end_datetime'] = res['start_datetime']
                                update_values[n]['state'] = 'available' if not is_partial else 'is_assigned'
                                break
                        else:
                            is_after = False
                            update_values[n] = self.with_context(result=result, is_after=is_after).update_values(
                                slot_id,
                                start_time,
                                res['start_datetime'],
                                'available')
        # Show unassigned role for the current period
        for role_id in role_ids.filtered(lambda x: x.id not in list(update_values.keys()) + to_remove):
            slot_id_before = self.env['planning.slot'].sudo().search(
                [('role_id.active', '=', True),
                 ('role_id', '=', role_id.id), ('end_datetime', '<=', x),
                 ('end_datetime', '>=', x + relativedelta(days=0, hour=0, hours=TZ - 3, minute=0, second=0))],
                order="end_datetime desc", limit=1)
            slot_id_after = self.env['planning.slot'].sudo().search(
                [('role_id.active', '=', True),
                 ('role_id', '=', role_id.id), ('start_datetime', '>=', x),
                 ('start_datetime', '<=', x + relativedelta(days=+1, hour=0, hours=TZ + 3, minute=0, second=0))],
                order="start_datetime asc",
                limit=1)
            update_values[role_id.id] = {
                'name': role_id.name,
                'role_id': role_id.id,
                'start_datetime': slot_id_before.end_datetime if slot_id_before else x + relativedelta(hours=TZ, hour=0,
                                                                                                       minute=0,
                                                                                                       second=0),
                'end_datetime': slot_id_after.start_datetime if slot_id_after else y + relativedelta(days=+1, hours=TZ,
                                                                                                     hour=0, minute=0,
                                                                                                     second=0,
                                                                                                     seconds=-1),
                'destination_zone': slot_id_before.destination_zone if slot_id_before else
                self.env['ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone'),
                'pick_up_zone': slot_id_after.pick_up_zone if slot_id_after else self.env[
                    'ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone'),
                'state': 'available',
            }
        ordered_values = sorted(update_values.values(), key=lambda x: x['state'])
        for affectation in ordered_values:
            if affectation['destination_zone'] == self.env['ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone'):
                slot_id_before = self.env['planning.slot'].sudo().search(
                    [('role_id.active', '=', True),
                     ('role_id', '=', affectation['role_id']), ('end_datetime', '<=', x),
                     ('end_datetime', '>=', x + relativedelta(days=0, hour=0, hours=TZ - 3, minute=0, second=0))],
                    order="end_datetime desc", limit=1)
                if slot_id_before:
                    affectation['start_datetime'] = slot_id_before.end_datetime
                    affectation['destination_zone'] = slot_id_before.destination_zone

            if affectation['pick_up_zone'] == self.env['ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone'):
                slot_id_after = self.env['planning.slot'].sudo().search(
                    [('role_id.active', '=', True), ('role_id', '=', affectation['role_id']),
                     ('start_datetime', '>=', x),
                     ('start_datetime', '<=', x + relativedelta(days=+1, hour=0, hours=TZ + 3, minute=0, second=0))],
                    order="end_datetime asc", limit=1)
                if slot_id_after:
                    affectation['end_datetime'] = slot_id_after.start_datetime
                    affectation['pick_up_zone'] = slot_id_after.pick_up_zone
        ordered_values = sorted(ordered_values, key=lambda x: x['start_datetime'])
        values_available = list(filter(lambda x: x['state'] == 'available', ordered_values))
        values_is_assigned = list(filter(lambda x: x['state'] == 'is_assigned', ordered_values))
        values_unaivalable = list(filter(lambda x: x['state'] == 'unaivalable', ordered_values))
        ordered_values = values_is_assigned + values_available + values_unaivalable
        deduplicate_values = list(
            OrderedDict((frozenset(item.items()), item) for item in ordered_values).values())
        unaivalable = []
        # Show unaivalable role for the current period
        for role_id in role_ids.filtered(
                lambda x: x.id in to_remove and x.id not in list(update_values.keys())):
            unaivalable.append({
                'name': role_id.name,
                'role_id': role_id.id,
                'state': 'unaivalable',
            })
        planning['planning_ids'] = [[0, 0, val] for val in deduplicate_values + unaivalable]
        return planning

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda x: x.env.company,
        required=True, index=True)
    resource_id = fields.Many2one('resource.resource', 'Resource',
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  group_expand='_read_group_resource_id')
    planning_ids = fields.One2many('auto.planning.line.wizard', 'planning_id', string='Plannings')
    index = fields.Integer()
    driver_id = fields.Many2one('res.partner', string="Driver", required=False, store=True)

    def update_values(self, slot_id, start_datetime, end_datetime, state):
        result = self._context.get('result', False)
        is_after = self._context.get('is_after', False)
        self._context.get('is_partial', False)
        to_compare_bool = slot_id.sale_line_id and slot_id.sale_line_id.order_id.destination_zone_id
        general_params = self.env['ir.config_parameter'].sudo().get_param(
            'etech_auto_planning.default_destination_zone')
        destination_zone = slot_id.sale_line_id.order_id.destination_zone_id.name if to_compare_bool else general_params
        if not is_after:
            destination_zone = self.env['ir.config_parameter'].sudo().get_param(
                'etech_auto_planning.default_destination_zone')
        role_values = result[slot_id.role_id.id]
        if is_after and result and len(
                role_values) > 1 and slot_id.sale_line_id and slot_id.sale_line_id.order_id.pick_up_zone_id:
            index = role_values.index(list(filter(lambda x: x['slot_id'] == slot_id.id, role_values))[0])
            if index + 1 < len(role_values):
                slot_id = self.env['planning.slot'].sudo().browse(role_values[index + 1]['slot_id'])
                pick_up_zone = slot_id.pick_up_zone
            else:
                pick_up_zone = self.env['ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone')
        else:
            if not is_after:
                pick_up_zone = slot_id.pick_up_zone
            else:
                pick_up_zone = self.env['ir.config_parameter'].sudo().get_param(
                    'etech_auto_planning.default_destination_zone')
        return {
            'name': slot_id.role_id.name,
            'role_id': slot_id.role_id.id,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'destination_zone': destination_zone,
            'pick_up_zone': pick_up_zone,
            'state': state,
        }

    def create_planning_slot(self, line_id, crm_id=None, role_id=False):
        """
        Create planning slot
        :rtype: object
        """
        record_id = self.env['crm.lead'].sudo().browse(crm_id or self._context.get('active_ids'))
        planning_slot_id = self.env['planning.slot'].search([('crm_lead_id','=',record_id.id)])
        if planning_slot_id:
            single_planning_slot_id = planning_slot_id[0]
            single_planning_slot_id.sudo().write({
                'role_id': role_id or self.planning_ids.filtered(lambda x: x.is_selected)[0].mapped('role_id').id or False,
                'sale_line_id': line_id.id
            })
        else:
            self.env['planning.slot'].with_context(create_from="crm.lead").sudo().create({
                # 'resource_id': self.resource_id.id,
                'role_id': role_id or self.planning_ids.filtered(lambda x: x.is_selected)[0].mapped('role_id').id or False,
                'start_datetime': record_id.pick_up_datetime,
                'end_datetime': record_id.pick_up_datetime + relativedelta(hours=+record_id.duration),
                'sale_line_id': line_id.id,
                'allocated_hours': record_id.duration,
                'pick_up_zone_id': record_id.pick_up_zone_id.id,
                'destination_zone_id': record_id.destination_zone_id.id,
                'pick_up_zone': record_id.pick_up_zone,
                'destination_zone': record_id.destination_zone,
                'estimated_kilometers': record_id.estimated_kilometers,
                'client_note': record_id.client_note,
                'crm_lead_id': record_id.id
            })

    def convert_lead_to_quotation(self, crm_id=False, role_id=False):
        """
        Convert lead to quotation
        :rtype: object
        """
        record_id = self.env['crm.lead'].sudo().browse(crm_id or self._context.get('active_ids'))
        partner_id = self.env['res.partner'].search([('email_normalized', '=', record_id.email_from),
                                                     ('id', '=', record_id.partner_id.id)],
                                                    limit=1) if record_id.email_from else False
        if not partner_id:
            record_id._handle_partner_assignment(create_missing=True)
            partner_id = record_id.partner_id
        else:
            record_id._handle_partner_assignment(force_partner_id=partner_id.id, create_missing=False)
        if not record_id.model_category_id:
            planing_role = role_id.role_id or self.planning_ids.filtered(lambda x: x.is_selected)[0].mapped('role_id')
            categories = planing_role.vehicle_id.model_id
            list_price = categories.category_id.list_price
        else:
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
            note_line = _('Pick up zone: %s - location: %s  %s %s') % (
                record_id.pick_up_zone or '',
                record_id.location_duration.name,
                fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                note)
            section_line = _('Section Client - Pick up zone: %s - location: %s  %s %s') % (
                record_id.pick_up_zone or '',
                record_id.location_duration.name,
                fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                note)
            kilometer = 1
        else:
            berline_found = list_price.filtered(
                lambda y: not y.is_location and y.resource_calendar_id.attendance_ids.filtered(
                    lambda z: z.dayofweek == str(day_spring) and z.hour_from <= float_hours < z.hour_to))
            if record_id.as_many_course:
                kilometer_many_course = record_id.others_destination.mapped('kilometers_estimted')
                if kilometer_many_course:
                    kilometer = sum(kilometer_many_course)
                note_line = _("Pickup zone: %s - Destination zone: %s. %s %s") % (
                    record_id.pick_up_zone,
                    " ,".join(record_id.others_destination.mapped('name')),
                    fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                    note
                )
                section_line = _("Section Client - Pickup zone: %s - Destination zone: %s. %s %s") % (
                    record_id.pick_up_zone,
                    " ,".join(record_id.others_destination.mapped('name')),
                    fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                    note
                )
            else:
                note_line = _('Pick up zone: %s (%s) - Destination zone: %s (%s) [%s] %s') % (
                    record_id.pick_up_zone_id.name or '', record_id.pick_up_zone,
                    record_id.destination_zone_id.name or '',
                    record_id.destination_zone,
                    fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                    note)

                section_line = _('Section Client - Pick up zone: %s (%s) - Destination zone: %s (%s) [%s] %s') % (
                    record_id.pick_up_zone_id.name or '', record_id.pick_up_zone,
                    record_id.destination_zone_id.name or '',
                    record_id.destination_zone,
                    fields.Datetime.context_timestamp(self, record_id.pick_up_datetime).strftime("%d/%m/%Y %H:%M"),
                    note)

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
                        xprice = self.env['area.time.wait.price'].sudo().search([
                            ('begin_wait_time', '<', xtime),
                            ('end_wait_time', '>=', xtime),
                            ('active', '=', True),
                        ])
                        price_wait_time += xprice and xprice.price or 0
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
                elif product.uom_id.name == 'km':
                    line_notes = note_line
                else:
                    line_notes = ''

                if product.time_wait_ok:
                    section_notes = section_note_wait
                elif product.uom_id.name == 'km':
                    section_notes = section_line
                else:
                    section_notes = ''

                # order_line += [
                #     (0, 0, {
                #         'name': product.name,
                #         'product_id': product.id,
                #         'product_uom_qty': my_kilometers,
                #         'product_uom': product.uom_po_id.id,
                #         'price_unit': price_units,
                #     })
                # ]
                if line_notes and section_notes:
                    order_line += [
                        (0, 0, {
                            'display_type': 'line_note',
                            'name': line_notes
                        }),
                        (0, 0, {
                            'display_type': 'line_section',
                            'name': section_notes})
                    ]
        else:
            raise ValidationError(_('no working vehicle on this day'))

        order_id = record_id.order_ids.filtered(lambda o: o.state == 'draft')[-1]
        if order_id:
            order_id.write({
                'order_line': order_line
            })
        else:
            order_id_new = self.env['sale.order'].create({
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
            order_id = order_id_new
        return order_id

    def validate(self):
        planning_id = self.planning_ids.filtered(lambda x: x.is_selected)
        if not planning_id:
            raise UserError(_("You must select a vehicle from the list to continue"))

        if len(self.planning_ids.filtered(lambda p: p.is_selected)) >= 2:
            raise UserError(_('A vehicle has already been selected, you cannot select multiple vehicles'))

        if self.driver_id:
            planning_id.role_id.vehicle_id.driver_id = self.driver_id.id
        # Convert lead to quotation
        order_id = self.convert_lead_to_quotation(role_id=planning_id)

        # update order_line :
        driver_notes =  _(
            'Driver name: %s - Car details: %s with the license plate: %s'
        ) % (
            self.driver_id.name,
            str(planning_id.role_id.vehicle_id.model_id.name + " " + planning_id.role_id.vehicle_id.model_id.brand_id.name),
            planning_id.role_id.vehicle_id.license_plate,
        )
        
        order_id.update({
            'order_line': [(0, 0, {
                            'display_type': 'line_section',
                            'name': driver_notes})],
        })

        # Create planning slot
        self.create_planning_slot(order_id.order_line[0])
        # Update lead status
        record_id = self.env['crm.lead'].sudo().browse(self._context.get('active_ids'))
        record_id.with_context(from_auto_planning=True).write({'stage_id': self.env.ref('crm.stage_lead2').id})
        # Set role on lead and order
        record_id.role_id = self.planning_ids.filtered(lambda x: x.is_selected)[0].mapped('role_id').id or False
        order_id.role_id = record_id.role_id.id
        action = self.env.ref('crm.crm_lead_action_pipeline').sudo().read()[0]
        return action

    def automatic_assignment(self, crm_id, phone):
        self = self.with_user(SUPERUSER_ID)
        partner = self.env['res.partner'].sudo()
        country_obj = self.env['res.country'].sudo()
        vehicle = self.env['fleet.vehicle'].sudo()
        driver_phone = format_phone_number(
            phone_number='0' + phone[-9:], country=country_obj.search([('code', '=', 'MG')]))
        driver_id = partner.search(['|', ('phone', '=', driver_phone), ('mobile', '=', driver_phone)])
        if not driver_id:
            raise ValueError(_('The %s is not assign to an driver on Odoo') % driver_phone)
        vehicle_id = vehicle.search([('driver_id', '=', driver_id.id)])
        if not vehicle_id:
            raise UserError(_('No vehicle found for the driver %s') % driver_phone)
        planning_id = self.env['planning.role'].sudo().search([('vehicle_id', 'in', vehicle_id.ids)])
        if not planning_id:
            raise UserError(_('No role found for the driver %s') % driver_phone)
        if len(planning_id) > 1:
            planning_id = planning_id[-1]
        # create order related to current lead
        order_id = self.sudo().convert_lead_to_quotation(crm_id=crm_id, role_id=planning_id)
        order_id.referrer_id = driver_id.id
        # create planning for this affectation
        self.create_planning_slot(order_id.order_line[0], crm_id, planning_id.id)
        crm_lead_id = self.env['crm.lead'].sudo().browse(crm_id)
        crm_lead_id.with_context(from_auto_planning=True).write({
            'stage_id': self.env.ref('crm.stage_lead2').id,
            'role_id': planning_id.id
        })
        order_id.role_id = planning_id.id


class AutoPlanningLineWizard(models.TransientModel):
    _name = 'auto.planning.line.wizard'
    _description = 'Auto Planning Line'
    _order = 'start_datetime'

    name = fields.Char()
    planning_id = fields.Many2one('auto.planning.wizard', string='Planning')
    pick_up_zone = fields.Text("Next destination")
    destination_zone = fields.Text("Last position")
    role_id = fields.Many2one('planning.role', string="Role")
    resource_id = fields.Many2one('resource.resource', 'Resource')
    start_datetime = fields.Datetime('Start Date')
    end_datetime = fields.Datetime('End Date')
    index = fields.Integer()
    state = fields.Selection(
        [('available', 'Available'), ('is_assigned', 'Is Assigned'), ('unaivalable', 'Unaivalable')])
    is_selected = fields.Boolean('Selected')
