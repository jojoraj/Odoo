# -*- coding: utf-8 -*-
{
    'name': "custom_project",

    'summary': """
      Restrict client access for project""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
          'project',
          'hr',
          'hr_timesheet',
          'igy_access',
          'base',
          'hr_skill',  
        ],

    # always loaded
    'data': [
        'views/account_analytic_line_job.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project.xml',
        'views/task.xml',
        'views/dashboard.xml',
        'views/menu.xml',
        'views/account_analytic_line_analysis_views.xml',
    ],
    # only loaded in demonstration mode
    'application': True,
    'installable': True
}
