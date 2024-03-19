# -*- coding: utf-8 -*-
{
    'name': "evtc_lmfs_map_bo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Back office Map render
    """,

    'author': "Ny Avo Kevin",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','fleet','web_map','evtc_lmfs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
    ],
    'assets':{
        'web.assets_backend': [
            'evtc_lmfs_map_bo/static/src/js/MapView/*',
        ],
        'web.assets_qweb': [
            'evtc_lmfs_map_bo/static/src/xml/**/*',
        ],
    }
}
