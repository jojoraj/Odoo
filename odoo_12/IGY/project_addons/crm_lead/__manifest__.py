# -*- coding: utf-8 -*-
{
    'name': 'Ingenosya CRM Lead',
    'version': '1.0',
    'description': 'CRM - Lead',
    'author': 'Ingenosya Madagascar',
    'sequence': 1,
    'website': 'https://www.ingenosya.mg',
    'depends': ['crm', 'igy_custom_crm'],

    # always loaded
    'data': [
        'views/crm_lead_view.xml',
    ],
    'installable': True,
    'application': True,
}
