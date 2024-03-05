# -*- coding: utf-8 -*-
{
    'name': "Igy Employee edit subskill only",

    'summary': """
        Employee update only""",

    'description': """
       
    """,

    'author': "Ingenosya",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'custom_hr_employee', 'hr_skill'],

    # always loaded
    'data': [
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml'
    ],

}