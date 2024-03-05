# -*- coding: utf-8 -*-
{
    'name': "ingenosya_meeting",

    'summary': """
        Géstion des salles de réunions
    """,

    'author': "Idéalison - Ingenosya",
    'website': "www.ingenosya.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [   
        'base',
        'web',
        'hr',
        'mail',
        'calendar',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/meeting_reservation.xml',
        'views/meeting_timezone.xml',
        'views/meeting_room.xml',
        'views/menu.xml',
        'views/templates.xml',
        'views/templates.xml',
        'data/cron.xml',
        'data/timezone.xml',
    ],
    # only loaded in demonstration mode
    'application': True,
    'installable': True
}