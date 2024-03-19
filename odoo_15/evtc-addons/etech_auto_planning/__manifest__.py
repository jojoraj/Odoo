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
{
    'name': "eTech Auto Planning",
    'summary': 'Manage Auto Planning',
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Sales/CRM',
    'version': '15.0.0.0.1',

    'depends': ['web',
                'planning',
                'crm',
                'sale_planning',
                'pos_sale',
                'esanandro_crm',
                'fleet',
                ],

    'data': [
        # Data
        'data/ir_config_parameter_data.xml',
        'data/data_route.xml',
        # Security
        'security/ir.model.access.csv',
        # Wizards
        'wizard/auto_planning_wizard_view.xml',
        'wizard/assign_wizard_views.xml',
        # Views
        'views/crm_lead_views.xml',
        'views/planning_role_views.xml',
        'views/sale_order_views.xml',
        'views/planning_slot_views.xml',
        'views/pos_config_view.xml',
        'views/pos_order_views.xml',
        'views/route_planning.xml',
        'views/res_partner_view.xml'
    ],
    'demo': [
    ],
    'sequence': -10,
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
    'assets': {
        'web.assets_backend': [
            'etech_auto_planning/static/src/js/planning_gantt_row.js',
        ],
        'point_of_sale.assets': [
            'etech_auto_planning/static/src/js/SaleOrderFetcher.js',
            'etech_auto_planning/static/src/js/SaleOrderRow.js',
            'etech_auto_planning/static/src/js/PaymentScreen.js',
            'etech_auto_planning/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'etech_auto_planning/static/src/xml/*',
        ],
    },
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
}
