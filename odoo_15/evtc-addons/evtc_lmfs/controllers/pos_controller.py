from odoo import http
from odoo.http import request, Response
import werkzeug
MAX_ATTEMPT = 20


class PosController(http.Controller):

    @http.route(['/pos/user'], type='http', auth="user", website=True)
    def get_pos_by_user(self, immatriculeID,**kw):
        role_by_immatricule = request.env['planning.role'].sudo().search([('vehicle_id.license_plate','=',immatriculeID)])
        if not role_by_immatricule:
            return Response(template='website.page_404', status=404)
        role_by_immatricule[0]
        current_pos = request.env['pos.config'].sudo().search([('role_id','=',role_by_immatricule.id)])
        if not current_pos:
            return Response(template='website.page_404', status=404)
        current_pos = current_pos[0]
        if current_pos.current_session_state == 'opened':
            val = current_pos.open_ui()
            return werkzeug.utils.redirect(val.get('url',''))
        if current_pos.current_session_state == 'opening_control':
            current_session = current_pos.current_session_id
            val = current_session.open_frontend_cb()
            return werkzeug.utils.redirect(val.get('url',''))
        if current_pos.current_session_state == 'closing_control':
            current_session = current_pos.current_session_id
            val = current_session.open_frontend_cb()
            return werkzeug.utils.redirect(val.get('url',''))
        if not current_pos.current_session_id and  not current_pos.pos_session_username:
            val = current_pos.open_session_cb()
            return werkzeug.utils.redirect(val.get('url',''))