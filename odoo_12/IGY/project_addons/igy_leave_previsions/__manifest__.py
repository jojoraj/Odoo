# -*- coding: utf-8 -*-
{
    'name': "igy_leave_previsions",

    'summary': """
        Prevision on leaves""",

    'author': "Rado - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'hr_holidays',
        'project_timesheet_holidays',
        'project_forecast',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml'  
    ],

    'application': True,
    'installable': True,
}
