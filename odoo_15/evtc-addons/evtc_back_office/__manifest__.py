{
    'name': "EVTC Back Office",

    'summary': """
        extend evtc front module
    """,
    'author': "Julien Etech-doo IT",
    'website': "http://www.etechconsulting-mg.com",

    'category': 'lead',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'esanandro_crm', 'account'],
    'data': [
        'views/crm_security.xml',
        'views/autocomplete_fields.xml',
        'views/account_move.xml',
    ],
    "assets": {
        "web.assets_common": [],
        "web.assets_backend": [
            'evtc_back_office/static/src/**/*.js',
            'evtc_back_office/static/src/**/*.scss',
        ],
        "web.assets_frontend": [],
        'web.assets_qweb': [
            'evtc_back_office/static/src/**/*.xml',
        ],
    }
}
