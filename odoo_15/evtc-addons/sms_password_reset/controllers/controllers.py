import logging

from odoo import http
from odoo.addons.auth_signup.controllers.main import \
    AuthSignupHome as AuthSignupHomeSuper
from odoo.addons.signup_validation_code.controllers.main import \
    AuthSignupHome as AuthSignupHomeVC
from odoo.http import request

from ..tools.phone_number import format_phone_number

_logger = logging.getLogger(__name__)

DONT_CHECK = ['lastname', 'firstname']
PASS_ERROR = "Assurez-vous que votre mot de passe contient au moins 8 caractères, un chiffre et une majuscule"
PHONE_ERROR = "Please use email if your country is not Madagascar"
FORMAT_ERROR = 'please check your phone number'
URL = "/web/reset_password?db={}&token={}"
WEB_URLS = "/web/reset_password/confirmation?login={}&token={}"
WITHOUT_FLAG = [699, 672, 61, 55, 246, 47, 1721, 508, 383, 594, 599]


class SmsPasswordReset(AuthSignupHomeSuper):

    @http.route('/web/reset_password/sms', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password_by_sms(self, *args, **kw):
        context = {
            'countries': request.env['res.country'].sudo().search([])
        }
        token = kw.get('token')
        if request.httprequest.method == 'POST':
            country_code = kw.get('country', 'MG')
            partner_phone = kw.get('phone', False)
            if country_code != 'MG' or not country_code:
                context['error'] = PHONE_ERROR
            else:
                country = request.env['res.country'].search([('code', '=', country_code)], limit=1)
                if not country:
                    context['error'] = 'Please select your country'
                try:
                    format_tmp = format_phone_number(partner_phone, country)
                    domain = [('phone', '=', format_tmp)]
                    partners = request.env['res.partner'].sudo().search(domain)
                    if partners and len(partners) >= 1:
                        user_id = partners.user_ids[0]
                        context['name'] = partners.user_ids[0].name
                        context['phone'] = partners.phone
                        context['company_code'] = request.website.company_id.company_code
                        context['token'] = token
                    else:
                        context['error'] = ""
                except Exception:
                    context['error'] = FORMAT_ERROR
                if 'error' not in context:
                    company_id = user_id.company_id
                    body = company_id.orange_sms_body
                    prefix_code = company_id.company_code
                    code, token = user_id.generate_confirmation_code()
                    body = body.format(user_id.name, '{}-{}'.format(prefix_code, code))
                    user_id.partner_id.signup_prepare()
                    user_id.send_orange_sms(body=body, force_send=True)
                    return request.redirect(WEB_URLS.format(user_id.partner_id.email, token))
        response = request.render('sms_password_reset.reset_by_sms', context)
        return response

    @http.route('/web/reset_password/confirmation', type='http', auth='public', website=True, sitemap=False)
    def reset_password_confirmation_code(self, *args, **kwargs):
        qcontext = {
            'company_code': request.website.company_id.company_code,
            'phone': kwargs.get('login', False),
            'token': kwargs.get('token', False),
        }
        return request.render('sms_password_reset.password_reset_verification_code', qcontext)

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        recursive_method = super(SmsPasswordReset, self).web_auth_signup(*args, **kw)
        if kw.get('reset_password', False):
            recursive_method.qcontext['reset_password'] = True
        else:
            recursive_method.qcontext['reset_password'] = False
        return recursive_method


class AuthSignupHomeCheckCode(AuthSignupHomeVC):

    @http.route('/json/check/code', type='json', auth='public', website='true')
    def web_check_code(self, token, code, **kwargs):
        response = super().web_check_code(token, code)
        if kwargs.get('default_sms', False) and 'url' in response:
            response['url'] += '&reset_password=True'
        return response
