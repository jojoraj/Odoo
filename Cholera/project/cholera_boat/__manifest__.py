# -*- coding: utf-8 -*-
{
    'name': "cholera_boat",

    'summary': """
    """,

    'description': """
    """,

    'author': "eTech consulting",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'cholera_sanitary_barrier', 'cholera_vehicle'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/flow_moov_view.xml',
        'views/fleet_crew.xml',
        'views/fleet_vehicle_inherit.xml',
        'views/vehicle_menu_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
