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
    'name': "evtc portal",
    'summary': 'Manage Basic Functionnality',
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Hidden',
    'version': '15.0.0.0.1',

    'depends': ['etech_base', 'evtc_front', 'portal', 'sale', 'pos_sale', 'esanandro_geotab', 'signup_validation_code'],

    'data': [
        'views/portal_templates.xml',
        'views/contact_templates.xml',
        'views/evtc_myaccount.xml',
        'views/evtc_list_course.xml',
        'views/crm_lead.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            "evtc_portal/static/src/js/**.js",
            "evtc_portal/static/src/scss/evtc_myaccount.scss",
        ],
    },
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
    'external_dependencies': {
        "python": ['mygeotab', 'phonenumbers'],
    },
}
