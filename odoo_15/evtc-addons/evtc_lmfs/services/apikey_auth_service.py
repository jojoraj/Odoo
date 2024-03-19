from odoo import _, models
from odoo.http import request
from odoo import SUPERUSER_ID
from werkzeug.exceptions import Unauthorized

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"
    _description = "HTTP Routing for ApiKey"

    @classmethod
    def _auth_method_lmfs_api_key(cls):
        api_header_key = request.httprequest.headers.get("api_key")
        api_params_key = request.params.get('api_key')
        api_key = api_header_key or api_params_key
        if not api_key:
            raise Unauthorized(_("Missing api_key"))
        odoo_api_key = request.env['middle.office'].sudo().get_api_key()
        if odoo_api_key and api_key != odoo_api_key.api_key:
            raise Unauthorized("API key invalid")
        request.uid = SUPERUSER_ID