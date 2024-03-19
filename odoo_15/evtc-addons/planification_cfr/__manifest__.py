##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2022 eTech Consulting (<http://www.etechconsulting-mg.com>). All Rights Reserved
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
{
    'name': "CFR Planning",
    'author': "eTech Consulting",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'Tools',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'evtc_crm', 'planning'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # Data
        'data/cron_planification_cfr.xml',
        # Views
        'views/res_config_settings_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/additional_trip_views.xml',
        'views/request_result_list.xml',
        'views/fuel_cost_views.xml',
        'views/templates_mail.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'planification_cfr/static/src/js/*',
        ],
        'web.assets_qweb': [
            'planification_cfr/static/src/xml/*',
        ],
    },
}
