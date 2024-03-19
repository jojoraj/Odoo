{
    'name': 'evtc taxi',
    'summary': ''' about taxi ville ''',
    'author': 'eTech Consulting',
    'website': 'https://www.etechconsulting-mg.com/',
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'fleet',
        'website_livechat',
        'etech_auto_planning',
        'restaurant_commission',
        'esanandro_crm',
        'evtc_portal',
        'vtc_area_destination',
        'middleoffice_connector',
        'etech_public_partner_image'
    ],
    'external_dependencies': {'python': ['jwt']},
    'data': [
        'data/crm_stage_data.xml',
        'data/data_type_vehicle.xml',
        'data/data_state_vehicle.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/list_course.xml',
        'views/fleet_vehicle_views.xml',
        'views/template.xml',
        'views/taxi_step_utils.xml',
        'views/taxi_step_templates.xml',
        'wizard/auto_planning_wizard_view.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'evtc_taxi/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            'evtc_taxi/static/src/scss/taxi.scss',
            'evtc_taxi/static/src/js/frontend/**/*',
        ],
        'web.assets_backend': [
            'evtc_taxi/static/src/js/backend/**/*'
        ],
    }
}
