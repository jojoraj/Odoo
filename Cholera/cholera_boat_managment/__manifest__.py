# -*- coding: utf-8 -*-
{
    'name': "cholera_boat_managment",

    'summary': """
    """,

    'description': """
    """,

    'author': "eTech Consulting",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'mail', 'covid_localisation'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/cholera_boat_menu_view.xml',
        'views/cholera_boat_form_view.xml',
        'views/cholera_boat_menu_model.xml',
        'views/cholera_boat_menu_type.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
