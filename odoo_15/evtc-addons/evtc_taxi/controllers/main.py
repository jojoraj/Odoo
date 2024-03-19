from odoo import http
from odoo.http import request

MAX_ATTEMPT = 20


class Quotation(http.Controller):

    @http.route(['/taxi-reservation/<model("crm.lead"):crm_lead_id>'], type='http', auth="user", website=True)
    def view_quotation(self, crm_lead_id, **kw):
        values = crm_lead_id.prepare_dashboard_values()
        progress_values = crm_lead_id.prepare_progress_values()
        values.update(progress_values)
        return request.render('evtc_taxi.reservation_taxi_step', values)
