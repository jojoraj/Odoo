# -*- coding: utf-8 -*-
{
    'name': "igy_badge",

    'summary': """
        badge updater""",

    'description': """
        this module will update and be able to adapt information of igy employee with the badge 
        update 
    """,

    'author': "Yvan Franco",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','mail','hr','web'],

    # always loaded
    'data': [
        'reports/igy_badge_report.xml',
        'reports/igy_badge_inherit.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}