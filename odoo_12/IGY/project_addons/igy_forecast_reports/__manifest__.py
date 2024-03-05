# -*- coding: utf-8 -*-
{
    'name': "igy_forecast_reports",

    'summary': """
        email higher managements about forecasts""",

    'author': "Rado - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'project_forecast',
        # TODO : make another modules for ingenosya's data
        'ingenosya_timesheet_reminder',
        'report_xlsx',
        'ingenosya_timesheet_reminder'
    ],

    'data': [
         'reports/report_forecast_xlsx.xml',
        'data/cron.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
    ],
}