# -*- coding: utf-8 -*-
{
    'name': "cholera_boat",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
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
        'views/flow_moov_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/fleet_vehicle.xml',
        'views/fleet_boat.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
