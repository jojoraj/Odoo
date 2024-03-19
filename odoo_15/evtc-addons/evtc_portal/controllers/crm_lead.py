import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class PartnerNotice(http.Controller):

    @route('/web/customer/review', type='json', auth='user', website=True)
    def account(self, crm_id, review_value=0, **post):
        crm = request.env['crm.lead'].sudo().browse(int(crm_id))
        data_review = False
        if crm:
            partner = request.env.user.partner_id
            crm.update({'partner_notice': str(review_value)})
            _logger.info(f'user {partner.name} sent {review_value}')
            data_review = True
        return data_review

    @route('/export/pdf', type='http', auth='user', website=True)
    def export_resume_pdf(self):
        pdf = request.env['report'].sudo().get_pdf([student_id], 'module_name.report_name', data=None)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
