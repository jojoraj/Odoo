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
    'name': "Mygeotab V1",
    'author': "Tokiniaina RAKOTOARISOA",
    'website': "http://www.etechconsulting-mg.com",

    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'contacts', 'fleet'],

    'data': [
        # Data
        # Views
        'views/fleet_vehicle_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mygeotabV1/static/src/js/map_renderer.js',
            'mygeotabV1/static/src/js/map_view.js'
        ],
        'web.assets_qweb': [
            'mygeotabV1/static/src/xml/**/*',
        ],
    },
    "external_dependencies": {
        "python": ['redis', 'mygeotab'],
    },
}
