# -*- coding: utf-8 -*-
{
    'name': "ingenosya_auto_leave_alloc",

    'summary': """
        Automatic leave allocations for Ingenosya employees""",

    'description': """
        Automatic leave allocations for Ingenosya employees
    """,

    'author': "Rado - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'hr_holidays',
    ],

    'data': [
        'data/leave_alloc_cron.xml',
        'data/decimal_precision.xml',

        'views/hr_leave_type_views.xml',
        'views/hr_views.xml',
    ],

    'application': True,
    'installable': True,
}