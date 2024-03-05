# -*- coding: utf-8 -*-
{
    'name': "igy_subskill",

    'summary': """
        Skills
    """,

    'description': """
        This module will upgrade skills and 
    """,

    'author': "Yvan Franco",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','mail','hr','hr_skill'],

    # always loaded
    'data': [
        'views/views.xml',
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],

    'installable': True,
    'auto_install': False
}