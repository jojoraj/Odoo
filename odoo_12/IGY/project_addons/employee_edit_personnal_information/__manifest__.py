# -*- coding: utf-8 -*-
{
    'name': "employee_edit_personnal_information",

    'summary': """
        Suivi du data des employees""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','custom_hr_employee'],

    # always loaded
    'data': [
        'views/employee.xml',

    ],
    # only loaded in demonstration mode
    'application':True,
    'installable': True
}