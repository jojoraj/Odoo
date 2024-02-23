# -*- coding: utf-8 -*-

{
     'name': 'my_module',
     'version': '12.0.1.0.0',
    'summary': 'Record Student Information',
    'category': 'Tools',
    'author': 'Niyas Raphy',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': ' Techno Solutions',
    'website': 'http://www.cybrosys.com',
    'depends': ['base', 'mail', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_view.xml',
        'views/sale_order_view.xml',
        'views/student_view_matricule.xml',
        'views/classe_view.xml'
    ],
    'images': '[]',
    'licence': 'AGPL-3',
    'installable': 'True',
    'application': 'False',
    'auto_install': 'False',
}
