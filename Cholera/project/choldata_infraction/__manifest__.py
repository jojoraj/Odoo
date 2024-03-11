# -*- coding: utf-8 -*-
{
    'name': "Cholera Infraction",

    'summary': """
        Cholera Infraction """,

    'description': """
        Cholera Infraction
    """,

    'author': "Etech",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['fleet', 'base', 'cholera_riposte'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/cholera_infraction_views.xml',
        'views/infraction_type_views.xml',
        'views/infraction_res_partner_views.xml',
        'views/infraction_fleet_vehicle_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': True,
}
