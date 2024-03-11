##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2024 eTech Consulting (<http://www.etechconsulting-mg.com>). All Rights Reserved
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
    'name': "Cholera Call",
    'summary': '''
        This module add a state of Cholera patient
        ''',
    'version': '16',
    'category': '',
    'sequence': -15,
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base'],
    'data': [
        # security
        # views
        'views/x_activite_suivi_inherit.xml',
        'views/res_partner_view_form.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
