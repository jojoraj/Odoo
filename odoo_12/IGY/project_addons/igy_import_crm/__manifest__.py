{
    'name': 'Igy Import Data',
    'version': '12.0.0.0',
    'summary': '',
    'description': '',
    'category': '',
    'author': '',
    'website': '',
    'license': '',
    'depends': [
        'smile_impex', 'hr', 'crm',
    ],
    'qweb': [
        "static/src/xml/button.xml",
    ],
    'data': [
        'data/ir_model_template.xml',
        'views/import_data_crm.xml',
        'views/template.xml'
    ],
    'installable': True,
    'auto_install': False
}