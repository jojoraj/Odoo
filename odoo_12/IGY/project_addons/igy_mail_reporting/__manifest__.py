# -*- coding: utf-8 -*-
{
    'name': "igy_mail_reporting",

    'summary': """
        Email reporting
    """,
    'author': "Stive - Ingenosya",
    'website': "www.ingenosya.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['crm', 'igy_custom_crm', 'mass_mailing', 'report_xlsx'],

    'data': [
        'views/crm_view_inherit.xml',
        'security/ir.model.access.csv',
        'data/mail_reporting_export.xml',
        'views/mail_reporting_view.xml',
        'views/mail_reporting_cold_view.xml',
        'reports/mail_report_pdf.xml',
        'reports/report.xml',
        'views/mailing_export.xml'
    ],

    'application': True,
    'installable': True
}
