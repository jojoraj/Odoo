import jwt
from odoo.addons.auth_odoo_jwt.datamodels.user_info import TokenResponse
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.http import request


class AuthServices(Component):
    _inherit = 'auth.services'

    @restapi.method(
        [(["/token"], "POST")],
        input_param=Datamodel("user.info"),
        output_param=Datamodel("token.response"),
        auth="public"
    )
    def get(self, user):
        result = super().get(user)
        validator_id = request.env.ref('auth_odoo_jwt.auth_odoo_jwt_validator')
        validator_id = validator_id.sudo()
        payload = validator_id._decode(str.encode(result.access_token))
        user_id = request.env['res.users'].sudo().browse(payload['user']['uid']).exists()
        if user_id:
            payload['user']['secretPassword'] = user_id.partner_id.secret_key
        src_pwd = user_id and user_id.partner_id.secret_key or ''
        access_token = jwt.encode(payload, validator_id.secret_key, algorithm="HS256")
        return TokenResponse(expire_in=result.expire_in, token_type="Bearer", access_token=access_token, secret_password=src_pwd)
