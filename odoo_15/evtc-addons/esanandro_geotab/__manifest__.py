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
    'name': "Evtc Résérvation",
    'author': "eTech Consulting",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'reservation',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'website', 'web', 'etech_fleet', 'sale_management', 'esanandro_crm', 'point_of_sale', 'etech_auto_planning'],
    'external_dependencies': {
        "python": ['geopy', 'mygeotab'],
    },
    'data': [
        'data/kpi_cron.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
        'views/trip_views.xml',
        'views/planning_role.xml',
        'views/sale_order_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            '/esanandro_geotab/static/src/js/pos_reserv_js.js',
            '/esanandro_geotab/static/src/js/geotab_pos_order_stop.js',
            '/esanandro_geotab/static/src/js/pos_button_localization.js',
            '/esanandro_geotab/static/src/js/SaleOrderManagementScreen.js',
        ],
        'web.assets_frontend': ['/esanandro_geotab/static/src/scss/geotab.scss',
                                '/esanandro_geotab/static/src/scss/esanandro_geotab.scss',
                                '/esanandro_geotab/static/src/js/geotab_web.js'],
        'web.assets_qweb': ['/esanandro_geotab/static/src/xml/pos_reserv_action_button.xml'],
    }
}
