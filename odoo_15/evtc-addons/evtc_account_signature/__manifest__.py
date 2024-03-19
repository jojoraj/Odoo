# -*- coding: utf-8 -*-
{
    'name': "evtc account signature",

    'summary': """
        customize account signature to evtc
    """,

    'author': "Etech consulting",
    'website': "http://www.etechconsulting-mg.com",

    'category': 'account',
    'version': '0.1.0',

    'depends': ['account_signature', 'evtc_invoice_data', 'invoice_report_customize'],

    # always loaded
    'data': [
        'report/account_report.xml',
    ],
}
