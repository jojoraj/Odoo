# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Access Rigths",
    "summary": "Manage the acces to the menu item for the module Timesheet",
    "version": "10.1.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": (
        "Odoo Community Association (OCA)"
    ),
    "website": "https://github.com/OCA/hr",
    "depends": [
        'project',
        'base',
        'web',
        'base', 
        "hr_timesheet",
        "project_timesheet_synchro",
        'hr', 
        'analytic',
        'uom',
    ],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/hr_timesheet.xml",
        "views/res_users.xml",
        "views/menu_timesheet_manager.xml",
        "views/menu.xml",
    ],
    'installable': True,
}