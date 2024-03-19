# -*- coding: utf-8 -*-
{
    'name': "EVTC LMFS",
    'summary': """
        * SIID or External ID of LMFS
        * Add auth method: lfms_api_key
    """,
    'author': "Etech Consulting",
    'website': "https://www.etechconsulting-mg.com",
    'category': 'Opportunity',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'base_rest',
        'crm',
        'etech_auto_planning',
        'middleoffice_connector',
        'point_of_sale',
        'vtc_area_destination',
        'evtc_portal',
        'web',
        'fleet',
        'web_map',
        'website'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/map_front_api.xml',
        'views/dis_api_keys.xml',
        'views/crm_lead_view.xml',
        'wizards/auto_planning_wizard_view.xml',
        'views/map_options.xml',
        'views/map_views.xml',
        'views/trip_list_views.xml',
        'views/progress_trip/index.xml',
        'views/progress_trip/step.xml',
        'views/res_partner.xml',
        'views/fleet_vehicle_view.xml'
    ],
    "assets": {
        'point_of_sale.assets': [
            'evtc_lmfs/static/src/js/PointOfSale/*',
        ],
        'web.assets_frontend': [
            # outer link
            "https://fonts.googleapis.com/css?family=Material+Icons",
            "https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css",
            "https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js",

            # module link
            'evtc_lmfs/static/src/js/frontend/**.js',

            #tracking link
            'evtc_lmfs/static/src/js/MapTracking/**.js',
            # tracking styles
            'evtc_lmfs/static/src/css/*',
            'evtc_lmfs/static/src/scss/*',
        ]
    },
    "external_dependencies": {
        "python": ['redis']
    }
}
