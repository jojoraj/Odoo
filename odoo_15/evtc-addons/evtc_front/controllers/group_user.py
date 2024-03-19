from odoo import http
from odoo.addons.phone_validation.tools import phone_validation
from odoo.http import request


class CreateByOtherUser(http.Controller):

    @http.route('/new/partner', type='json', auth='user')
    def new_partner(self, params_id=None, **kwargs):
        noupdate = False
        partner_id = request.env.user.partner_id
        partner_obj = request.env['res.partner'].sudo()
        partner_ids = kwargs.get('partner_id', False)
        country = kwargs.get('country_id', False)
        email = kwargs.get('email', False)
        tel = kwargs['phone']
        values = {
            'name': kwargs['name'],
            'company_type': 'person',
            'phone': tel,
            'origin_partner_id': partner_id.id
        }
        erreur = {'arch': False, 'details': None, 'id': None}
        country_id = request.env['res.country'].sudo().search([('code', 'ilike', country)], limit=1)
        if not country_id:
            erreur.update({
                'details': 'Le Champs pays n\'a pas été renseignér, veuillez le definir'
            })
            return erreur
        try:
            format_tmp = phone_validation.phone_format(tel, country_id.code, country_id.phone_code)
        except Exception as j:
            erreur.update({
                'details': str(j)
            })
            return erreur
        values.update({
            'country_id': country_id.id,
            'phone': format_tmp,
        })
        existing_phone = partner_obj.search(['|', ('phone', '=', format_tmp), ('mobile', '=', format_tmp)])
        if existing_phone and len(existing_phone) > 1:
            details = [f'{rec.name} : {rec.phone or rec.mobile}' for rec in existing_phone]
            erreur.update({
                'details': ', \n'.join(details)
            })
            return erreur
        elif existing_phone:
            user_link = request.env['res.users'].sudo().search([('partner_id', '=', existing_phone.id)])
            if user_link:
                noupdate = True
            params_id = existing_phone.id

        if email:
            values['email'] = email
            existing_email = partner_obj.search([('email', '=', email)])
            if existing_email and len(existing_email) > 1:
                details = [f'{z.name}, {z.email}' for z in existing_email]
                erreur.update({
                    'details': ', '.join(details)
                })
                return erreur
        try:
            if partner_ids:
                partner = request.env['res.partner'].browse(partner_ids)
                result = partner.id
            elif params_id:
                del values['phone']
                if not noupdate:
                    request.env['res.partner'].sudo().browse(params_id).write(values)
                result = params_id
            else:
                new_partner = partner_obj.create(values)
                result = new_partner.id
        except Exception as r:
            erreur.update({
                'details': str(r)
            })
            return erreur
        return {'arch': True, 'details': None, 'id': result}

    @http.route('/update/partner', type='json', auth='user')
    def update_partner(self, **kwargs):
        partner_id = request.env.user.partner_id
        values = {}
        partner_ids = kwargs.get('partner_id', False)
        res = {'arch': True, 'details': None, 'id': None}
        if not partner_ids:
            if kwargs['name'] != partner_id.name:
                values.update({'name': kwargs['name']})
            if kwargs['phone'] != partner_id.mobile:
                values.update({'mobile': kwargs['phone']})
            if values:
                partner_id.write(values)
        else:
            partner = request.env['res.partner'].sudo().browse(partner_ids)
            res.update({
                'id': partner.id
            })
            return res
        res.update({
            'id': partner_id.id
        })
        return res
