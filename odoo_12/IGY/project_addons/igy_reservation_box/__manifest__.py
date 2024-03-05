# -*- coding: utf-8 -*-
{
    'name': "Ingenosya réservation box internet",
    "sequence": 4,

    'summary': """
        Géstion de réservation de box internet
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Ingenosya",
    'website': "www.ingenosya.com",

    'category': 'Uncategorized',
    'version': '12.1.0.0',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'data/timezone_data.xml',
        'views/box_material_views.xml',
        'views/box_timezone_view.xml',
        'views/box_reservation_views.xml',
        'views/views.xml',
    ],
}
