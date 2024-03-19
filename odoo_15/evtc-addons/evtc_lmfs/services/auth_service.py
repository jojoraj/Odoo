from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import AccessDenied
from odoo import _
from odoo.http import request
import phonenumbers
import logging
from passlib.hash import pbkdf2_sha512

_logger = logging.getLogger(__name__)

def format_phone_number(phone_number, country):
        try:
            # phone_number = str(phonenumbers.parse(phone_number).national_number)
            phone_parse = phonenumbers.parse(phone_number, region=country.code, keep_raw_input=True)
            phone_number = str(phone_parse.raw_input)
        except Exception as e:
            _logger.info('phone_number not formatted : {}'.format(e))

        return phone_validation.phone_format(
            phone_number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format='INTERNATIONAL',
            raise_exception=True
        )

class AuthService(Component):
    _inherit = 'base.rest.service'
    _name = 'auth.service'
    _usage = 'auth'
    _collection = 'custom.auth.service'
    _description = """ Authenticate Odoo """

    def _res_auth(self):
        return {
            'code': {'type': 'integer'},
            'status': {'type': 'string'},
            'message': {'type': 'string'},
        }


    @restapi.method(
    [(['/login'], 'POST')],
    input_param=Datamodel('auth.input'),
    output_param=restapi.CerberusListValidator('_res_auth'),
    auth='none',type='http',webite=False
    )
    def authenticate(self, body):
        res = []
        try:
            login = body.login
            password = body.password
            if not login or not password:
                res = [{
                    'code': 400,
                    'status': 'Bad request',
                    'message': 'Missing parameter in the body'
                }]
                return res
            
           
            country_id = request.env['res.country'].sudo().search(
                    [('code', '=', 'MG')])
            phone_result = format_phone_number(login,country_id)
            user = self.env['res.users'].sudo().search([('login', '=', phone_result)])
            if user:
                user = user.with_user(user)
                check = user._check_credentials(password,{'interactive': True})   
                return [{
                    'code': 200,
                    'status': 'Success',
                    'message': 'OK'
                }]
            else:                
                return [{
                    'code': 400,
                    'status': 'Failed',
                    'message': 'Login not present in odoo'
                }]
        except AccessDenied:
            return [{
                        'code': 400,
                        'status': 'Failed',
                        'message': 'Access denied'
                    }]
        except Exception as e:
            res = [{
                'code': 404,
                'status': 'Failed',
                'message': str(e)
            }]
            return res
