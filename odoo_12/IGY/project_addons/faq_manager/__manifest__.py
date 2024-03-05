# -*- coding: utf-8 -*-
{
    'name': "faq_manager",

    'summary': """
        Gestion des FAQ""",

    'description': """
        -  Création menu gestion FAQ
        -  Gestion manuel des  FAQ  par les administrateur(RH / DP / CP / Admin)
        -  Filtre des FAQ
        -  Affichage des FAQ pour les simples utilisateurs
        -  Commentaires des FAQ par les simples utilisateurs
    """,

    'author': "Ingenosya (Idéalison)",
    'website': "http://www.ingenosya.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/faq_views.xml',
        'views/faq_models_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
