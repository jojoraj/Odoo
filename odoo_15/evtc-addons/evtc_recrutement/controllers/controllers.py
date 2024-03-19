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
from odoo.addons.website_hr_recruitment.controllers.main import \
    WebsiteHrRecruitment
from odoo.http import request


class EvtcRecrutement(http.Controller):
    @http.route('/my/applicants', type='http', auth="user", website=True, csrf=False)
    def my_appliants(self, **kw):
        user_id = request.env.user.id
        applicant_id = request.env['hr.applicant'].sudo().search([('user_id.id', '=', user_id)])
        if applicant_id:
            values = {
                'applicants': applicant_id,
            }
        else:
            values = {}

        return request.render('evtc_recrutement.my_list_of_appliant', values)

    @http.route('/create/post', type='http', methods=['POST'], auth="user", website=True, csrf=False)
    def create_post(self, **kw):
        if kw:
            description_html = ("""<section class="pt32">
                                    <div class="container">
                                        <div class="row">
                                            <div class="col-lg-8 pb32">
                                                <p class="lead">
                                                    {}
                                                    <br/>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                               </section>""").format(kw['description'] if kw['description'] else '')
            request.env['hr.job'].sudo().create({
                'name': kw['job'] if kw['job'] else '',
                'description': kw['description'] if kw['description'] else '',
                'website_description': description_html,
                'address_id': int(kw['company_id']) if kw['company_id'] else False,
                'user_id': request.env.user.id,
                'website_published': True,
            })
            return request.redirect('/jobs')


class VtcWebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/company/<int:office_id>',
    ], type='http', auth="public", website=True, sitemap=WebsiteHrRecruitment.sitemap_jobs)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        result = super(VtcWebsiteHrRecruitment, self).jobs(country=country, department=department, office_id=office_id, **kwargs)
        return result
