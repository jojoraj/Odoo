# -*- coding: utf-8 -*-
{
    'name': "igy_project_report",

    'summary': """
        Email reports of dashboard project
    """,

    'author': "Rivo Lalaina - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'project',
        'sale_timesheet',
        'custom_project',
        'report_xlsx',
        
    ],

    'data': [
        'reports/report_project_xlsx.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/mail_template.xml',
        'views/project_form_view.xml',
    ],
}

