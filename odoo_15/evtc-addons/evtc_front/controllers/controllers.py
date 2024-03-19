from odoo import http
from odoo.http import request


class EvtcFront(http.Controller):

    @http.route('/reservation', auth='user', website="True", sitemap=True)
    def evtc_reservation(self, **kw):
        vehicle_category_ids = http.request.env['fleet.vehicle.model.category'].sudo().search([],
                                                                                              order='qualification_level')
        favorite_address = http.request.env.user.partner_id.child_ids.filtered(
            lambda x: x.type == 'other' and x.is_favorites)
        child_ids = http.request.env.user.partner_id.child_ids
        historic = child_ids.filtered(lambda x: x.type == 'other' and x.is_historical).sorted(lambda c: c.write_date,
                                                                                              reverse=True)[:5]
        google_api_keys = request.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        groups_user = request.env.user.has_group('evtc_front.reservation_for_others')
        values = {
            'vehicle_category_ids': vehicle_category_ids,
            'favorite_address': favorite_address,
            'historic': historic,
            'google_maps_api_key': google_api_keys,
            'user_access': groups_user,
            'countries': request.env['res.country'].sudo().search([]),
            'partner': request.env.user.partner_id or None
        }
        return http.request.render("evtc_front.index", values)

    @http.route('/evtc/save_address/', type='json', auth='user', website=True)
    def save_address(self, street, name='', is_favorites=False, is_historical=False, instruction='', **post):
        if street:
            values = {
                'type': 'other',
                'is_favorites': is_favorites,
                'is_historical': is_historical,
                'latitude': post.get('latitude', ''),
                'longitude': post.get('longitude', ''),
                'comment': instruction
            }
            partner_id = request.env.user.partner_id
            country = request.env.user.company_id.country_id.name
            splitted = street.split(',')
            splitted = [place.strip() for place in splitted]
            if country in splitted:
                values.update({'country_id': request.env.user.company_id.country_id.id})
                splitted.remove(country)
            if country and len(splitted) > 1:
                values.update({'city': splitted[-1]})
            values.update({
                'street': ", ".join(splitted) if splitted else country,
                'name': name if name else ", ".join(splitted)
            })
            request.env['res.partner'].add_new_contact(partner_id, values)
            return {'result': 200}

    @http.route('/user/info/', type="json", auth='public')
    def get_user_info(self, **kw):
        user = http.request.env.user.partner_id
        return {'work_phone': user.mobile or user.phone, 'name': user.name, 'id': user.id}

    @http.route('/web/get/usd-euro/currency-id', type='json', auth='public')
    def get_usd_euro_value(self):
        return request.env['res.currency'].sudo().get_unit_per_mga()

    @http.route('/session-log', type='json', auth='user')
    def google_session_token_store(self, recuperation=0, destination=0, isValidate=False, myaccount_service=0):
        record = request.env['google.log_session'].sudo()
        partner_id = http.request.env.user.partner_id
        value = {
            'recuperation_with_validation': 0,
            'destination_with_validation': 0,
            'recuperation_without_validation': 0,
            'destination_without_validation': 0,
            'record_crm_validation': 0,
            'details_callback': 0,
            'myaccount_with_validation': 0,
            'myaccount_without_validation': 0,
        }
        if isValidate:
            value['recuperation_with_validation'] = recuperation
            value['destination_with_validation'] = destination
            value['myaccount_with_validation'] = myaccount_service
            value['record_crm_validation'] = 1
        else:
            value['recuperation_without_validation'] = recuperation
            value['destination_without_validation'] = destination
            value['myaccount_without_validation'] = myaccount_service
        value['details_callback'] = value['recuperation_with_validation'] + value['destination_with_validation'] + \
            value['recuperation_without_validation'] + value['destination_without_validation'] + \
            value['myaccount_without_validation'] + value['myaccount_with_validation']
        record.find_current_data(partner_id.id, value)

    def get_html_view(self, partner):
        details = partner.name
        if partner.phone:
            details += "( %s )" % partner.phone
        return f""" <li class="list-group-item oe_partner_select oe_hover" partner_id="{partner.id}"
                        style="cursor:pointer; text-align: center;"><p>{details}</p></li>"""

    def create_partner_view(self):
        return """  <li class="list-group-item oe_add_partner oe_hover" data-toggle='modal' data-target='#create_new_contact'
                        style="cursor:pointer; text-align: center;"> <p> Ajouter </p> </li>"""

    def template_views(self, opp_part):
        return {
            'id': opp_part.id,
            'nameLower': opp_part.name.lower(),
            'name': opp_part.name,
            'phone': opp_part.phone or opp_part.mobile,
            'html_viewer': self.get_html_view(opp_part),
        }

    @http.route('/web/partners', type='json', auth='user')
    def render_partner_name(self):
        partner = request.env['res.partner'].sudo().search([('type', '=', 'contact')])
        partner_to_filter = request.env.user.has_group('evtc_front.reservation_for_others') and [self.template_views(o) for o in partner] or []
        return {'create_views': self.create_partner_view()}, partner_to_filter

    @http.route('/web/partners/phone', type='json', auth='user')
    def render_partner_details(self, partner_id=''):
        if partner_id:
            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            _dic = {'name': partner.name, 'phone': partner.phone, 'id': partner.id}
            return _dic
        else:
            return {'name': None, 'phone': None, 'id': None}
