{
    'name': "esanandro marketing keycloak",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "etech",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'users',
    'version': '15.0.0.0.1',
    "license": "AGPL-3",
    'depends': ['base', 'orange_sms', 'mail', 'keycloak_oidc'],
    'data': [
        'data/cron_marketing.xml',
        'security/ir.model.access.csv',
        'data/marketing_mail.xml',
        'views/users_views.xml',
        'views/config.xml',
    ],
}
