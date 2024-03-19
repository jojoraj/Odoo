##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import http
from odoo.http import request


class EvtcPub(http.Controller):
    @http.route('/render/view/publicity', type='json', auth="public", website=True)
    def render_view_publicity(self):
        view_sudo = request.env['ir.ui.view'].sudo()
        values = dict(
            evtc_button_menu_ids=request.env['evtc.button.menu'].sudo().search([]),
            list_video=request.env['evtc.pub'].sudo().search([]),
        )
        return view_sudo._render_template("evtc_publicity.publicity_main_template", values)

    @http.route('/register/rating', type='json', auth='public', website=True)
    def create_rating(self, **kw):
        if not request.session.uid:
            res_id = request.env.company.id
            res_model_id = request.env.ref('base.model_res_company').sudo().id
            rating_obj = request.env['rating.rating'].sudo()
            clientoption = kw.get('rating')
            rating_obj.create({
                'partner_id': request.env.user.partner_id.id,
                'rating': clientoption.get('rate', 0),
                'res_id': res_id,
                'res_model_id': res_model_id,
                'opinions': clientoption.get('Opinion', '')
            })
        return

    @http.route('/send/mail', type='json', auth='public', website=True)
    def send_mail_idea(self, **kw):
        if not kw.get('ideas', False):
            return {'data': False}
        ideas = kw.get('ideas', False)
        email_from = kw.get('mail', False)
        company_id = request.website.company_id
        template_id = request.env.ref('evtc_publicity.evtc_pub_email_template').sudo()
        if company_id and template_id:
            mail = template_id.sudo().with_context(**dict(email_from=email_from, ideas=ideas)).send_mail(company_id.id, force_send=True)
            mail_id = request.env['mail.mail'].sudo().browse(mail)
            if mail_id and mail_id.state in ['sent', 'received']:
                return {'data': True}
            else:
                return {'data': False}

    @http.route('/count/click', type='json', auth='public', website=True)
    def number_click(self, **kw):
        if kw.get('id', False):
            evtc_button_id = request.env['evtc.button.menu'].sudo().browse(kw.get('id', False))
            if evtc_button_id.exists():
                evtc_button_id.number_click += 1
