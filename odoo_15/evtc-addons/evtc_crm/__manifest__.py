{
    'name': "evtc_crm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "etech consulting-mg",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'crm',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'crm', 'etech_fleet', 'esanandro_crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
