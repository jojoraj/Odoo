# -*- coding: utf-8 -*-
{
    'name': "Igy Purchase Custom",

    'summary': """
       Demande d'achats Ingenosya""",


    'author': "Rivo et Idéalison - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase','mail','purchase_stock'
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml', 
        'views/purchase_order_form.xml' ,
        'views/purchase_order_tree.xml',
        'views/product_template_add_vendor.xml',
    ],

    # only loaded in demonstration mode
    'application':True,
    'installable': True
}
