{
    'name': 'Ingenosya Stock',
    'version': '1.0.0.0',
    'summary': 'This module inherit Stock modules',
    'description': """ 
        This module allow to:
         - scan employee on picking
         - link a picking with employee
    """,
    'category': '',
    'author': '',
    'website': '',
    'license': '',
    'depends': ['base', 'stock', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_history_type.xml',
        'data/product_template_type.xml',
        'data/function.xml',
        'views/assets.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/product_history_type_views.xml',
        'views/product_template_type_views.xml',
        'views/product_template_type_menu_views.xml',

    ],
    'installable': True,
    'auto_install': False,
}
