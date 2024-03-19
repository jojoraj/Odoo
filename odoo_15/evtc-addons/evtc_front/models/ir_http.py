##############################################################################
#
#    Odoo
#    Copyright (C) 2017 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        """
            add the google map api key in context
            in the http rendering of a web client
            return: dict
        """
        rendering_context = super(Http, self).webclient_rendering_context()
        rendering_context['google_maps_api_key'] = request.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        return rendering_context
