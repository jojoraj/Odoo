# -*- coding: utf-8 -*-
{
    'name': "Igy Payroll",

    'summary': """
       Paiement ingenosya""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance', 'project', 'hr_holidays','mail', 'hr_timesheet', 'timesheet_grid'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/igy_employee_report.xml',
        'views/employee_payroll_view.xml',
        'views/employee.xml',
        'data/mail_data.xml',

    ],
    # only loaded in demonstration mode
    'application':True,
    'installable': True
}