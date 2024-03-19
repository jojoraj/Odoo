{
    'name': "fuel management",
    'summary': """ """,
    'author': "etech",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'fleet',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['fleet', 'esanandro_geotab', 'fleet_security'],
    'external_dependencies': {
        "python": ['mygeotab'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/cron_geotab_fuel.xml',
        'data/fleet_service_type.xml',
        'views/views.xml',
        'views/res_config_settings.xml',
    ],
}
