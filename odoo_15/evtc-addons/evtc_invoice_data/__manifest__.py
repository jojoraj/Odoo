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
    'name': "evtc invoice information",
    'summary': 'Manage Basic Functionnality',
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': '',
    'version': '15.0.0.0.1',
    "license": "AGPL-3",
    'depends': ['base', 'web', 'planning', 'account', 'sale', 'esanandro_geotab', 'pos_sale'],

    'data': [
        'views/evtc.xml',
        'views/res_company_views.xml',
        'views/report_invoice.xml',
        'views/base_document_layout_views.xml',
        'views/account_move_views.xml',
        'report/report_consolidate.xml',
    ],
}
