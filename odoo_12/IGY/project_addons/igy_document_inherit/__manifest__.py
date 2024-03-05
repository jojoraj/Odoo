{
    'name': 'Igy Document',
    'version': '12.0.0.0',
    'summary': 'This module inherit document modules',
    'description': '',
    'category': '',
    'author': 'Ingenosya',
    'website': 'https://www.ingenosya.mg',
    'license': '',
    'depends': ['documents', 'web','mail'],
    'data': [
        'data/data.xml',
        'views/assets.xml',
        'views/menu.xml',
    ],
    'qweb': [
        'static/src/xml/documentViewer.xml',
    ],
    'installable': True,
    'auto_install': False,
}
