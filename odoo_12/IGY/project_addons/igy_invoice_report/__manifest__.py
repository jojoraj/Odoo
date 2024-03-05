# -*- coding: utf-8 -*-

{
    'name': "igy_invoice_report",

    'summary': """
        Ingenosya Invoice Report""",


    'author': "Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'sale'],

    # always loaded
    'data': [
        'views/invoice_sequence_views.xml',
        'views/sale_configuration_views.xml',
        'views/account_invoice_views.xml',
        'views/default_invoice_report.xml',
        'views/account_report_igy.xml',
        'views/report_account_igy.xml',
        'views/sale_order.xml',
        'views/sale_order_report.xml',
        'views/res_partner.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'application': False,
    'installable': True
}