# -*- coding: utf-8 -*-
{
    'name': "Alterning mail server",
    'icon': '/igy_alterning_mail_server/static/description/icon.png',
    'sequence': 10,
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ingenosya Madagascar",
    'website': "https://www.ingenosya.mg",
    'category': 'Tools',
    'version': '12.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/alterning_mail_server.xml',
        'data/mail_log_config_server.xml',
        'data/ir_cron.xml',
        'views/alterning_mail_server_views.xml',
        'views/ir_mail_log_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
