# -*- coding: utf-8 -*-

import base64
from odoo.http import Controller, request, route
from werkzeug.utils import redirect

DEFAULT_IMAGE = '/igy_theme/static/src/img/fond.jpg'

class DasboardBackground(Controller):

    @route(['/dashboard'], type='http', auth='user', website=False)
    def dashboard(self, **post):
        user = request.env.user
        company = user.company_id
        if company.dashboard_background:
            image = base64.b64decode(company.dashboard_background)
        else:
            return redirect(DEFAULT_IMAGE)

        return request.make_response(
            image, [('Content-Type', 'image')])