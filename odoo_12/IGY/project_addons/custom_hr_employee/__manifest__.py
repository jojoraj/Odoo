# -*- coding: utf-8 -*-
{
    'name': "custom_hr_employee",

    'summary': """
        Activation du pin""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance', 'project', 'hr_holidays', 'hr_timesheet', 'timesheet_grid', 'hr_holidays'],

    # always loaded
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/presence.xml',
        'views/tags.xml',
        'views/hr_leave.xml',
        'views/hr_department.xml',
        'data/information_theme_data.xml',
        # 'views/igy_employee_report.xml',
        # 'views/employee_payroll_view.xml',

    ],
    # only loaded in demonstration mode
    'application':True,
    'installable': True
}
