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
    'name': "invoice report customize",
    'summary': 'customize invoice report',
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'views/res_company_view.xml',
        'views/res_bank_view.xml',
        'report/invoice_report.xml',
    ],
}
