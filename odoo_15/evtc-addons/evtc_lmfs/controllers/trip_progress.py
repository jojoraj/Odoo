from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID

MAX_ATTEMPT = 20


class Quotation(http.Controller):

    @http.route(['/trip-reservation/<int:crm_lead_id>'], type='http', auth="user", website=True)
    def view_quotation(self, crm_lead_id, **kw):
        opportunity_id = request.env['crm.lead'].sudo().browse(crm_lead_id)
        values = opportunity_id.prepare_dashboard_values()
        progress_values = opportunity_id.with_user(SUPERUSER_ID).prepare_progress_values()
        values.update(progress_values)
        values['dis_api_keys'] = request.env['ir.config_parameter'].sudo().get_param('evtc_lmfs.map_front_api_key')
        values['trackingID'] = opportunity_id.get_opportunity_tracking()
        return request.render('evtc_lmfs.reservation_trip_step', values)
