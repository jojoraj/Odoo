# -*- coding: utf-8 -*-
{
    'name': "ingenosya_timesheet_reminder",

    'summary': """
        Rappel sur les feuilles de temps
    """,

    'author': "Rado  - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [ 
        'base',
        'hr_holidays',
        'hr_timesheet',  
        'project_timesheet_holidays',
        'custom_hr_employee'
    ],

    'data': [
        'data/timesheet_cron.xml',
        'data/ir_cron.xml',
        'data/mail_template_reminder.xml',
        'data/hr_data.xml',
         'security/ir.model.access.csv',
        'views/public_holiday_views.xml',
        'views/hr_timesheet_readonly.xml',
        'views/hr_employee_begin_work.xml'
       
    ],

    'application': True,
    'installable': True,
}
