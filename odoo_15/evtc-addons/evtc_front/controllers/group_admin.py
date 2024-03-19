from odoo import _, http
from odoo.addons.phone_validation.tools import phone_validation
from odoo.http import request


class CreateByAdminGroup(http.Controller):

    @http.route('/web/partners/new', type='json', auth='user')
    def create_partner(self, name='', tel='', country_code='', email=''):
        vals = {
            'name': name,
            'phone': tel,
            'type': 'contact',
        }
        _errors = {}
        if not request.env.user.has_group('evtc_front.reservation_for_others'):
            _errors.update({'stat': 'failed', 'error': _("You don't have any permission to create other partner")})
            return _errors
        country = request.env['res.country'].sudo().search([('code', 'ilike', country_code)], limit=1)
        if country:
            vals.update({
                'country_id': country.id
            })
        partner = request.env['res.partner'].sudo()
        try:
            phone = phone_validation.phone_format(tel, country.code, country.phone_code)
            exist_phone = partner.search(['|', ('phone', '=', phone), ('mobile', '=', phone)])
            if exist_phone:
                _errors.update({'stat': 'failed', 'error': _('contact already exists')})
                contact = {
                    'name': ', \n'.join([f'{o.name}: {o.phone or o.mobile}' for o in exist_phone]),
                    'phone': exist_phone.mapped('phone'),
                }
                _errors.update({'details': contact})
                return _errors
            vals.update({
                'phone': phone
            })
        except Exception as e:
            _errors.update({
                'stat': 'failed', 'error': str(e), 'details': {'name': str(e)}
            })
            return _errors
        if email:
            existing_mail = partner.search([('email', '=', email)])
            if existing_mail:
                _errors.update({
                    'stat': 'failed', 'error': 'Mail already exists',
                    'details': {'name': ', \n'.join([f'{o.name}: {o.email}' for o in existing_mail])}
                })
                return _errors
            vals.update({
                'email': email
            })

        # create contact
        try:
            partner_id = partner.create(vals)
        except Exception as e:
            part = partner.search(['|', ('phone', '=', phone if phone else tel), ('mobile', '=', phone if phone else tel)])
            for j in part:
                request.env.cr.execute(f"delete from res_partner where id={j.id}")
            _errors.update({
                'stat': 'failed', 'error': 'Erreur',
                'details': {
                    'name': str(e),
                }
            })
            return _errors
        _errors.update({
            'stat': 'success', 'error': '',
            'details': {
                'name': partner_id.name,
                'phone': partner_id.phone,
                'id': partner_id.id,
            }
        })
        return _errors
