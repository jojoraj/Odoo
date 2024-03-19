{
    'name': "fleet_security",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "eTechConsulting",
    'website': "https://www.etechconsulting-mg.com",

    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'fleet'],
    'data': [
        'security/groups.xml',
        'views/menu.xml'
    ]
}
