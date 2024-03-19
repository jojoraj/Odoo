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
    'name': "Esanandro Parc Auto",


    'author': "eTech Consulting",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'fleet', 'product', 'resource', 'account_minimum_price'],

    'data': [
        # Data
        "security/ir.model.access.csv",
        # Views
        'views/fleet_vehicle_model_views.xml'
    ],
}
