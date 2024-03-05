{
    'name': 'Financial Purchase Module',
    'version': '12.0.0.0',
    'summary': '',
    'description': 'This module customize the purchase app on financial database',
    'category': 'purchase',
    'author': '',
    'website': '',
    'license': '',
    'depends': ['base', 'purchase', 'account'],
    'data': [
        'views/purchase_order_views.xml',
        'views/menu_sequence.xml'
    ],
    'installable': True,
    'auto_install': False,
}