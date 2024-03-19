import logging
import re
from datetime import datetime, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)

STATE_LABEL = {
    'in_progress': 'En cours de validation',
    'validate': 'Validée',
    'terminate': 'Terminée',
    'refused': 'Refusée',
    'unknown': 'Inconnue',
    'on_ride': 'En cours',
    'unpaid': 'A payer'
}
STATE = {
    'crm.stage_lead1': 'in_progress',
    'crm.stage_lead2': 'validate',
    'esanandro_crm.stage_lead7': 'validate',
    'crm.stage_lead3': 'on_ride',
    'esanandro_crm.stage_lead5': 'refused',
    'esanandro_crm.stage_lead6': 'terminate',
    'crm.stage_lead4': 'terminate',
    'evtc_lmfs.unpaid': 'unpaid'
}


class Lead(models.Model):
    _inherit = 'crm.lead'

    #          Google map javascript widget
    # ========================================
    attachment_maps = fields.Char()
    pick_up_zone = fields.Char()
    # ========================================
    reference_code = fields.Char()
    payment_method_note = fields.Char()
    vehicle_note = fields.Char()
    phone_in_moment = fields.Char()
    maps_image = fields.Image()
    model_category_id = fields.Many2one('fleet.vehicle.model.category')
    estimated_price = fields.Char(string='Price For Estimated Kilometer')

    @api.model
    def create(self, values):
        res = super(Lead, self).create(values)
        res.reference_code = f'L{res.id}'
        return res

    @api.model
    def create_crm_lead(self, lead):
        if not lead:
            return
        partner_id = self.env['res.partner'].sudo().browse(lead['partner_id']).exists()

        fmt = "%Y-%m-%d %H:%M:%S"
        local_datetime = datetime.strptime(lead['pick_up_datetime'], fmt)
        result_utc_datetime = local_datetime + timedelta(minutes=lead['off_set'])
        del lead['off_set']
        result_utc_datetime.strftime(fmt)
        lead['maps_image'] = bytes(lead['maps_image'].split('base64,')[1], 'utf-8') if lead['maps_image'] else False

        is_location = bool(lead.get('is_location'))

        try:
            h, m = re.findall("([0-9]+)", lead['duration'])
        except Exception:
            m = re.findall("([0-9]+)", lead['duration'])[0]
            h = None
        if h and m:
            t = timedelta(hours=int(h), minutes=int(m))
        else:
            t = timedelta(minutes=int(m))
        seconds = t.seconds
        minutes = seconds / 3600
        lead.update({
            'name': partner_id.name,
            'phone': partner_id.phone,
            'duration': minutes,
            'pick_up_datetime': result_utc_datetime,
            'is_location': is_location,
        })
        crm_record = self.sudo().create(lead)
        return crm_record.id

    def get_formatted_date(self, date):
        user_ids = self.partner_id.user_ids
        admin_tz = self.env['res.users'].browse(2).tz
        user_tz = user_ids[0].tz if user_ids and user_ids[0].tz else admin_tz
        local = pytz.timezone(user_tz)
        new_date = pytz.utc.localize(date).astimezone(local)
        return datetime.strftime(new_date, '%d-%m-%Y à %H:%M')

    def prepare_dashboard_values(self):
        if self.pick_up_datetime:
            date_pick_up = self.pick_up_datetime
        else:
            date_pick_up = datetime.now()

        user_tz = self.env.user.tz or pytz.utc.zone
        local = pytz.timezone(user_tz)

        create_date = pytz.utc.localize(self.create_date).astimezone(local)
        date_pick_up = pytz.utc.localize(date_pick_up).astimezone(local)
        date_destination = (date_pick_up + timedelta(hours=self.duration))
        date_pickup_formatted = date_pick_up.strftime('%d/%m/%Y')
        datetime_pickup_formatted = date_pick_up.strftime('%H:%M')
        duration = f'{int(self.duration)}h:{int((self.duration * 60) % 60)}min'
        real_duration = f'{int(self.real_duration)}h:{int((self.real_duration * 60) % 60)}min'
        kilometers = self.estimated_kilometers
        revenue = formatLang(self.env, self.expected_revenue, currency_obj=self.partner_id.currency_id)
        revenue = f'~ {revenue}'
        duration = duration
        real_duration = real_duration
        state = STATE.get(self.sudo().state_value, 'unknown')
        if state == 'on_ride':
            state = 'validate'
        # =========================================================
        # find the invoice link to the crm_id
        url_id = ''
        with_download = ''
        domain = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.env['sale.order'].sudo().search(domain)
        if orders:
            if len(orders) > 1:
                orders = orders[0]
            url = self.env['pos.order'].sudo().search(
                [('lines.sale_order_origin_id', 'in', orders.ids)]).account_move
            if url:
                url_id += url.access_url
                with_download += url.access_url
            if url and url.access_token:
                url_id += f'?{url.access_token}&'
                with_download += f'?{url.access_token}&'
            else:
                url_id += '?'
                with_download += '?'
            with_download += 'report_type=pdf&download=true'

        # =========================================================
        if state == 'terminate':
            order_confirmed = self.order_ids.filtered(lambda o: o.state == 'sale')
            kilometers = order_confirmed.real_distance
            try:
                linked_orders = order_confirmed.pos_order_line_ids.mapped('order_id')
                if linked_orders:
                    real_cost_value = sum(linked_orders.mapped('amount_paid'))
                else:
                    real_cost_value = order_confirmed.real_cost
                revenue = formatLang(self.env, float(real_cost_value), currency_obj=self.partner_id.currency_id)
            except Exception:
                revenue = formatLang(self.env, 0, currency_obj=self.partner_id.currency_id)
            duration = f'{int(order_confirmed.real_duration)}h:{int((order_confirmed.real_duration * 60) % 60)}min'
            date_destination = (date_pick_up + timedelta(hours=order_confirmed.real_duration))

        def get_street(full_address):
            return full_address.split(',')[0] if full_address and ',' in full_address else full_address

        formatted_pick_up_destination = _('%s to %s') % (
            datetime_pickup_formatted, date_destination.strftime('%H:%M'))
        destination_datetime = date_destination.strftime(_('%d/%m/%Y to %H:%M'))
        _create_date = create_date.strftime('%d/%m/%Y')
        _create_datetime = create_date.strftime('%H:%M')
        try:
            formatted_phone = self.partner_id._phone_format(self.phone_in_moment)
        except Exception as e:
            _logger.info(str(e))
            formatted_phone = self.phone_in_moment

        pick_up_zone = get_street(self.pick_up_zone)
        try:
            review = self.partner_notice == '0' and True or False
        except Exception as e:
            _logger.info(f'crm lead has no attribute partner_notice {str(e)}')
            review = False
        if self.as_many_course:
            destination_zone = self.others_destination.mapped('name')[-1]
        elif self.is_location:
            destination_zone = ''
        else:
            destination_zone = get_street(self.destination_zone)
        crm_time_wait = ''
        if self.as_many_course:
            times = 0
            for t in self.others_destination:
                times += t.wait_time.wait_time_mn
            if times > 0:
                h, m = str(times // 60), str(times % 60)
                hours = len(h) > 1 and h + ' h' or '0' + h + ' h'
                minutes = len(m) > 1 and m + ' mn' or '0' + m + ' mn'
                crm_time_wait += hours + ' ' + minutes
        crm_note = int(self.partner_notice) + 1
        vehicle_id = self.role_id.sudo().vehicle_id if self.role_id else False
        crm_data = {
            'crm_code': self.reference_code if self.reference_code else f'L{self.id}',
            'pick_up_zone': pick_up_zone if pick_up_zone else '',
            'destination_zone': destination_zone if destination_zone else '',
            'pick_up_date': date_pickup_formatted if date_pickup_formatted else '',
            'create_date': _create_date,
            'create_datetime': _create_datetime,
            'pick_up_datetime': datetime_pickup_formatted if datetime_pickup_formatted else '',
            'formatted_pick_up_destination': formatted_pick_up_destination,
            'destination_datetime': destination_datetime,
            'kilometers': kilometers,
            'revenue': revenue if revenue else '',
            'duration': duration,
            'real_duration': real_duration,
            'state': state,
            'state_label': STATE_LABEL[state],
            'payment_method_note': self.payment_method_note if self.payment_method_note else '',
            'vehicle_note': self.vehicle_note if self.vehicle_note else '',
            'driver_name': vehicle_id.driver_id.name if vehicle_id and vehicle_id.driver_id else '',
            'driver_image': vehicle_id.driver_id.image_128 if vehicle_id and vehicle_id.driver_id else '',
            'driver_phone': vehicle_id.driver_id.phone if vehicle_id and vehicle_id.driver_id else '',
            'license_plate': vehicle_id.license_plate if vehicle_id else '',
            'phone_in_moment': formatted_phone if self.phone_in_moment else '',
            'crm_id': self.id,
            'own_review': review,
            'recordset': self,
            'maps_image': bool(self.maps_image),
            'is_location': self.is_location,
            'crm_note': crm_note,
            'crm_time_wait': crm_time_wait,
            'invoices_url': url_id if url_id != '' else '#',
            'invoices_download': with_download if with_download != '' else '#',
            'client_name': self.partner_id.name
        }
        if crm_data.get('state', '') == 'refused':
            crm_data.update({
                'refusal_remarque': self.refusal_remark
            })
        if self.as_many_course:
            crm_data['destination_zone'] = self.others_destination.mapped('name')[-1]

        return crm_data

    @api.model
    def save_coordonate(self, args):
        if args:
            lng = args.get('lng')
            lat = args.get('lat')
            lead_id = args.get('id', False)
            zone = args.get('pick_up_zone')
            if lead_id:
                rec = self.sudo().search([('id', '=', lead_id)])
                rec.sudo().write({'pick_up_lat': lat,
                                  'pick_up_long': lng,
                                  'pick_up_zone': zone})
        if rec.sudo().dest_lat and rec.sudo().dest_long:
            return {'zone_nb': 2,
                    'pick_up_zone': rec.pick_up_zone,
                    'pick_up_lat': rec.pick_up_lat,
                    'pick_up_lng': rec.pick_up_long,
                    'destination_zone': rec.destination_zone,
                    'dest_lat': rec.dest_lat,
                    'dest_long': rec.dest_long
                    }
        else:
            return {'zone_nb': 1,
                    'pick_up_zone': rec.pick_up_zone,
                    'pick_up_lat': rec.pick_up_lat,
                    'pick_up_lng': rec.pick_up_long}

    @api.model
    def save_destination(self, args):
        if args:
            lng = args.get('lng')
            lat = args.get('lat')
            lead_id = args.get('id')
            rec = self.sudo().search([('id', '=', lead_id)])
            rec.sudo().write({'dest_lat': lat,
                              'dest_long': lng})
        if rec.pick_up_lat and rec.pick_up_long:
            return {'zone_nb': 2,
                    'pick_up_zone': rec.pick_up_zone,
                    'pick_up_lat': rec.pick_up_lat,
                    'pick_up_lng': rec.pick_up_long,
                    'destination_zone': rec.destination_zone,
                    'dest_lat': rec.dest_lat,
                    'dest_long': rec.dest_long}
        else:
            return {'zone_nb': 1,
                    'destination_zone': rec.destination_zone,
                    'dest_lat': rec.dest_lat,
                    'dest_long': rec.dest_long}

    @api.model
    def save_distance_duration(self, args):
        if args:
            distance = args.get('distance')
            duration = args.get('duration')
            lead_id = args.get('id')
            rec = self.sudo().search([('id', '=', lead_id)])
            rec.duration = duration
            rec.estimated_kilometers = distance
            return {
                'type': 'ir.actions.act_view_reload',
            }

    @api.model
    def getcoordinate(self, args):
        if args:
            lead_id = args.get('id')
            rec = self.sudo().search([('id', '=', lead_id)])
            if rec.pick_up_zone and rec.pick_up_lat and rec.pick_up_long and rec.dest_lat and rec.dest_long and rec.destination_zone:
                return {'pick_up_zone': rec.pick_up_zone,
                        'pick_up_lat': rec.pick_up_lat,
                        'pick_up_lng': rec.pick_up_long,
                        'destination_zone': rec.destination_zone,
                        'dest_lat': rec.dest_lat,
                        'dest_long': rec.dest_long}
