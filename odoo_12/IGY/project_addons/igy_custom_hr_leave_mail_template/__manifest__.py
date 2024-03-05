# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr_ leave mail template",
    "summary": "Customize email template for employees's leave",
    "version": "10.1.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": (
        "Rivo - INGENOSYA"
    ),
    "website": "https://github.com/OCA/hr",
    "depends": [       
       'mail', 'base', 'base_setup',
    ],
    'data': [
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'application': True ,
}
