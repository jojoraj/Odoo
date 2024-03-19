##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech Consulting (<http://www.etechconsulting-mg.com>). All Rights Reserved
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
    'name': "Esanandro CRM",

    'author': "eTech Consulting",
    'website': "http://www.etechconsulting-mg.com",

    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    "license": "AGPL-3",
    'depends': ['base', 'contacts', 'crm'],

    'data': [
        # Data
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/ir_action_data.xml',
        'data/sms_data.xml',
        'data/mail_data.xml',
        # Security
        'security/ir.model.access.csv',
        # Views
        'wizard/crm_refusal_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/localisation_views.xml',
        'views/crm_refusal_views.xml',
        'views/evtc_notification.xml',

        # search view

        'views/crm_code_seach_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'esanandro_crm/static/src/scss/assignment_reminder.scss',
            'esanandro_crm/static/src/js/activity_cell.js',
            'esanandro_crm/static/src/js/activity_filter_click.js'
        ]
    }
}
