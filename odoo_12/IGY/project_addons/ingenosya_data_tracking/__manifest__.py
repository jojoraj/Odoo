# -*- coding: utf-8 -*-
{
    'name': "ingenosya_data_tracking",

    'summary': """
        Suivi du data des employees""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/data_rate.xml',
        'views/data_tracking_employee.xml',
        'views/data_tracking_individual.xml',
        'views/cron.xml',

    ],
    # only loaded in demonstration mode
    'application':True,
    'installable': True
}