import logging
import math
from datetime import datetime, timedelta

import phonenumbers
from odoo import _, http, tools
from odoo.addons.evtc_front.models.crm_lead import STATE, STATE_LABEL
from odoo.addons.phone_validation.tools import phone_validation
from odoo.addons.portal.controllers.portal import \
    CustomerPortal as CustomerPortalBase
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.tools.image import image_data_uri

_logger = logging.getLogger(__name__)

MONTH = 'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split(
    '_')
WITHOUT_FLAG = [699, 672, 61, 55, 246, 47, 1721, 508, 383, 594, 599]
WEB_URLS = "/web/reset_password/confirmation?login={}&token={}"


class CustomerPortal(CustomerPortalBase):
    EVTC_MANDATORY_BILLING_FIELDS = ["name", "lastname"]  # "phone", "country_code" => champ grisé
    EVTC_OPTIONAL_BILLING_FIELDS = ["firstname", "email", "reset_pwd"]

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        partner_id = request.env.user.partner_id
        # Get All Pos Order for current partner

        def get_sum_hours_mn(object):
            hours, minutes = [], []
            for record in object:
                h, m = convert_float_time(record)
                hours.append(h)
                minutes.append(m)
            return sum(hours), sum(minutes)

        def convert_float_time(times):
            factor, val = times < 0 and -1 or 1, abs(times)
            return factor * int(math.floor(val)), int(round((val % 1) * 60))

        def convert_time_string(hours, minutes):
            minute = minutes % 60
            hour = (minutes // 60 + hours) % 24
            day = (minutes // 60 + hours) // 24
            ts = ''
            if day and day > 0:
                ts += f'{day}j '
            ts += f'{hour}h {minute}mn'
            return ts

        domain = [
            '&', ('state', '=', 'invoiced'),
            '|', ('partner_id.origin_partner_id', '=', partner_id.id)
            , ('partner_id.origin_partner_id', '=',
                  False), ('partner_id', '=', partner_id.id)
        ]


        reservation_ids = request.env['pos.order'].sudo().search(domain)
        reservation_number = len(reservation_ids)
        since_date = partner_id.create_date
        linked_order_ids = request.env['sale.order'].sudo()
        for reserve in reservation_ids:
            linked_order_ids += reserve.lines.mapped('sale_order_origin_id')
        sum_total_km = sum(linked_order_ids.mapped('real_distance'))
        total_km = float("{:.2f}".format(sum_total_km))
        reservation_complete_times = []
        for record in reservation_ids:
            reservation_complete_times.append(record.account_move.real_duration
                                              and record.account_move.real_duration or record.account_move.duration)
        t_hours, t_mins = get_sum_hours_mn(reservation_complete_times)
        # Get last CRM for current partner
        last_crm = request.env['crm.lead'].sudo().search([
            ('partner_id', '=', partner_id.id),
            ('partner_id.origin_partner_id', 'in', [False, partner_id.id]),
        ]).sorted(lambda c: c.id, reverse=True).filtered(
            lambda c: c.create_date > request.env.user.create_date)
        crm_data = dict()
        if last_crm:
            last_crm = last_crm[0]
            crm_data = last_crm.prepare_dashboard_values()

        values = {
            'reservation_number': reservation_number,
            'reservation_km_formatted': _(f'{total_km} Km'),
            'reservation_hour_formatted': convert_time_string(t_hours, t_mins),
            'signup_month': _('depuis %s %s') % (MONTH[since_date.month - 1], since_date.year),
            'crm_data': crm_data,
            'image_data_uri': image_data_uri
        }
        return request.render("evtc_portal.my_account_template", values)

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            if post.get('reset_pwd'):
                try:
                    confirmation_mode = post.get('confirmation_code', False)
                    if confirmation_mode and confirmation_mode == 'phone':
                        user_id = request.env.user
                        company_id = user_id.company_id
                        body = company_id.orange_sms_body
                        prefix_code = company_id.company_code
                        code, token = user_id.generate_confirmation_code()
                        body = body.format(user_id.name, '{}-{}'.format(prefix_code, code))
                        user_id.send_orange_sms(body=body, force_send=True)
                        return request.redirect(WEB_URLS.format(user_id.partner_id.email, token))
                    elif confirmation_mode and confirmation_mode == 'email':
                        request.env.user.action_reset_password()
                    else:
                        values['reset_password_error'] = 'No email or phone found'
                    values['reset_password_success'] = _(
                        'An email has been sent to you to reset your password')
                except Exception as e:
                    values['reset_password_error'] = e
            else:
                post['name'] = (post.get('lastname', '') + ' '
                                + post.get('firstname', '')).strip()
                error, error_message = self.details_form_validate(post)
                values.update({'error': error, 'error_message': error_message})
                if 'email' in post.keys():
                    del post['email']
                if 'phone' in post.keys():
                    del post['phone']
                values.update(post)
                if not error:
                    values = {key: post[key]
                              for key in self.EVTC_MANDATORY_BILLING_FIELDS + self.EVTC_OPTIONAL_BILLING_FIELDS if
                              key in post}
                    if values.get('country_code'):
                        country = request.env['res.country'].search([('code', '=', values.get('country_code'))])
                        values.pop('country_code')
                        values['country_id'] = country.id
                        values['firstname'] = post.get('firstname', '')
                        values['lastname'] = post.get('lastname', '')

                    partner.sudo().write(values)
                    if redirect:
                        return request.redirect(redirect)
                    return request.redirect('/my/account')
        try:
            phone = phonenumbers.parse(partner.phone).national_number
        except Exception:
            phone = partner.phone
            _logger.info('invalid phone')
        values.update({
            'partner': partner,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'has_mail': partner.email,
            'countries': request.env['res.country'].sudo().search([('phone_code', 'not in', WITHOUT_FLAG)],
                                                                  order='sequence, name')
        })
        if phone:
            values['phone'] = phone

            response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.EVTC_MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        email_exist = False
        if data.get('email'):
            email_exist = request.env['res.partner'].sudo().search([('email', '=', data.get(
                'email')), ('id', '!=', request.env.user.sudo().partner_id.sudo().id)])
        if email_exist or data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            if email_exist:
                error_message.append(
                    _(u'Un autre utilisateur utilise déjà cet email.'))
            else:
                error_message.append(
                    _('Invalid Email! Please enter a valid email address.'))

        # phone validation
        try:
            if data.get('country_code', False):
                country = request.env['res.country'].sudo().search([('code', '=', data.get('country_code'))])
                data['phone'] = phone_validation.phone_format(
                    data.get('phone'),
                    country.code if country else request.env.company.country_id.code,
                    country.phone_code if country else request.env.company.country_id.phone_code,
                    force_format='INTERNATIONAL',
                    raise_exception=True
                )
                if request.env['res.users'].sudo().search(
                        [('login', '=', data['phone']), ('id', '!=', request.env.user.sudo().id)]):
                    error["phone"] = 'error'
                    error_message.append(u'Numéro déjà existant.')
        except Exception:
            error["phone"] = 'error'
            error_message.append(
                _('Invalid phone number! Please enter a valid phone number.'))

        # vat validation
        partner = request.env.user.partner_id
        if data.get("vat") and partner and partner.vat != data.get("vat"):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")),
                                                                                   data.get("vat"))
                    partner_dummy = partner.new({
                        'vat': data['vat'],
                        'country_id': (int(data['country_id'])
                                       if data.get('country_id') else False),
                    })
                    try:
                        partner_dummy.check_vat()
                    except ValidationError:
                        error["vat"] = 'error'
            else:
                error_message.append(
                    _('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.EVTC_MANDATORY_BILLING_FIELDS + self.EVTC_OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    def generate_course_list(self, date_begin, date_end, sortby, page, status=None, **kw):
        _items_per_page = int(request.env['ir.config_parameter'].sudo(
        ).get_param('evtc_portal.course_per_page', 20))
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id
        CrmLead = request.env['crm.lead'].sudo()
        stage = request.env['crm.stage'].search_read([], fields=['id', 'name'])

        domain = [
            '|', ('partner_id.origin_partner_id', '=', partner_id.id),
            '&', ('partner_id', '=', partner_id.id),
            ('partner_id.origin_partner_id', '=', False)
        ]

        if request.env.user.partner_id.is_company:
            company_b2b_id = request.env.user.partner_id
            partner_child_b2b = request.env['res.partner'].sudo().search([
                ('related_company', '=', company_b2b_id.id)
            ])
            
            # Create a domain to filter crm.lead records based on partner_id
           
            if partner_child_b2b:
                # If partner_child_b2b is found, add its ids to the domain
                origin_partner_domain = [partner_id.id] + partner_child_b2b.ids
                partner_id_domain =  [partner_id.id] + partner_child_b2b.ids
                domain = [
                    '|', ('partner_id.origin_partner_id', 'in', origin_partner_domain),
                    '&', ('partner_id', 'in', partner_id_domain),
                    ('partner_id.origin_partner_id', '=', False)
                ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        stage_label = []
        state_terminate_ids, applicated_label_state = [], []
        state_validate_ids, validate_label_state = [], []
        for rec in stage:
            rec_id = int(rec.get('id'))
            xml = request.env['crm.stage'].browse(rec_id)._get_external_ids().get(rec_id)
            if xml:
                xml_id = xml[0]
            else:
                continue
            state = STATE.get(xml_id, False)
            if state and state == 'unpaid' and request.env.user.partner_id.company_type != 'company':
                continue
            if state and state in ['on_ride', 'validate']:
                state_validate_ids += [rec_id]
                validate_label_state += [{'id': rec_id, 'name': STATE_LABEL['validate']}]
            elif state and state != 'terminate':
                stage_label += [{'id': rec_id, 'name': STATE_LABEL[state]}]
            elif state:
                state_terminate_ids += [rec_id]
                applicated_label_state += [{'id': rec_id, 'name': STATE_LABEL[state]}]
        
        if state_terminate_ids and len(state_terminate_ids) > 1:
            stage_label += [applicated_label_state[0]]
        if state_validate_ids and len(state_validate_ids) > 1:
            stage_label += [validate_label_state[0]]
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']
        if date_begin and date_end:
            domain += [('create_date', '>=', date_begin), ('create_date', '<=', date_end)]
        elif date_begin:
            domain += [('create_date', '<', date_begin + timedelta(days=1)), ('create_date', '>', date_begin - timedelta(days=1))]
        elif date_end:
            domain += [('create_date', '<', date_end + timedelta(days=1)), ('create_date', '>', date_end - timedelta(days=1))]
        if status:
            status_id = int(status)
            if status_id in state_validate_ids:
                data_stage_ids = state_validate_ids
            elif status_id in state_terminate_ids:
                data_stage_ids = state_terminate_ids
            else:
                data_stage_ids = [status_id]
            domain += [('stage_id', 'in', data_stage_ids)]
        # count for pager
        crm_count = CrmLead.search_count(domain)
        pager = portal_pager(
            url="/my/course",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=crm_count,
            page=page,
            step=_items_per_page
        )

        crm_leads = CrmLead.search(
            domain, order=sort_order, limit=_items_per_page, offset=pager['offset']).filtered(
            lambda c: c.create_date > request.env.user.create_date)
        crm_data = [crm.prepare_dashboard_values() for crm in crm_leads]
        values.update({
            'date': date_begin,
            'crm_leads': crm_data,
            'page_name': 'course',
            'pager': pager,
            'default_url': '/my/course',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'stages': stage_label,
            'current_status': status
        })
        return values

    @route(['/my/course', '/my/course/page/<int:page>'], type='http', auth='user', website=True)
    def list_course(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self.generate_course_list(date_begin=date_begin, date_end=date_end, sortby=sortby, page=page, **kw)
        return request.render("evtc_portal.list_course_template", values)

    @route(['/my/course/search'], type='json', auth='user', website=True)
    def filter_list_course_json(self, page=1, date_begin=None, date_end=None, sortby=None, statusId=None, **kw):
        date_format = '%Y-%m-%d'
        if date_begin and isinstance(date_begin, str):
            date_begin = datetime.strptime(date_begin, date_format)
        if date_end and isinstance(date_end, str):
            date_end = datetime.strptime(date_end, date_format)
        values = self.generate_course_list(date_begin=date_begin, date_end=date_end, sortby=sortby, page=page, status=statusId, **kw)
        views = request.env['ir.ui.view'].sudo()._render_template('evtc_portal.list_course_template', values=values)
        return {'html_render': views}


class Contact(http.Controller):

    @route('/my/contact', type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        contact_ids = partner.child_ids
        values = {
            'partner': partner,
            'addresses': contact_ids.filtered(lambda contact: contact.latitude and contact.longitude).sorted(
                lambda c: c.write_date, reverse=True),
            'google_maps_api_key': request.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        }
        response = request.render('evtc_portal.my_contact_itg', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/my/contact/delete', type='http', methods=['POST'], website=True, auth='user', csrf=False)
    def delete_contact(self, **kwargs):
        contact_id = kwargs.get('contact_id', False)
        partner_id = request.env.user.partner_id
        if contact_id:
            contact_id = request.env['res.partner'].sudo().browse(
                int(contact_id))
            if contact_id and contact_id in partner_id.child_ids:
                contact_id.write({'active': False})

    @http.route('/my/contact/save', type='http', methods=['POST'], website=True, auth='user', csrf=True)
    def save_contact(self, **kwargs):
        partner_id = request.env.user.partner_id
        partner_obj = request.env['res.partner'].sudo()
        contact_id = kwargs.get('contact_id', False)
        latitude = kwargs.get('latitude', False)
        longitude = kwargs.get('longitude', False)
        comment = kwargs.get('comment', False)
        street = kwargs.get('location', False)
        country = request.env.user.company_id.country_id.name
        name = kwargs.get('name', False)
        values = {
            'latitude': latitude,
            'longitude': longitude,
            'comment': comment,
            'name': name,
            'is_historical': False,
            'is_favorites': True,
            'type': 'other'
        }
        splitted = street.split(',')
        splitted = [place.strip() for place in splitted]
        if country in splitted:
            values.update(
                {'country_id': request.env.user.company_id.country_id.id})
            splitted.remove(country)
        if country and len(splitted) > 1:
            values.update({'city': splitted[-1]})
            splitted.pop(-1)
        street = ", ".join(splitted) if splitted else country
        values.update({'street': street})
        operation = "create" if not contact_id else "write"
        if contact_id:
            contact_id = int(contact_id)
            is_child = contact_id in partner_id.child_ids.mapped('id')
            do_write = operation == 'write' and is_child
            if do_write:
                contact_update_id = partner_obj.browse(contact_id)
                contact_update_id.write(values)
        do_create = operation == 'create'
        if do_create:
            values.update({
                'parent_id': partner_id.id,
            })
            partner_obj.create(values)
        return request.redirect('/my/contact')
