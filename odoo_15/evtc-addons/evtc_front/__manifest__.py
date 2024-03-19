{
    'name': "evtc_front",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "etech",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'crm', 'website', 'web', 'fleet', 'website'],
    'data': [
        # user groups
        'views/website_many2many_views.xml',
        "views/evtc_groups.xml",
        "views/others_information_partner.xml",
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/snippets.xml',
        'views/layout.xml',
        'views/web_layout_api_keys.xml',
        'views/res_partner_coordinate.xml',
        'views/user_session.xml',
        'views/crm_lead_views.xml'
    ],
    "external_dependencies": {
        "python": ['redis', 'mygeotab'],
    },
    # only loaded in demonstration mode
    "assets": {
        "web.assets_common": [
        ],
        "web.assets_backend": [],
        "web.assets_frontend": [
            # wiget
            "evtc_front/static/src/js/widget/**.js",

            # google map
            "evtc_front/static/src/js/gmaps/**.js",

            # mixins
            "evtc_front/static/src/js/EvtcMixins/**.js",

            # Area
            "evtc_front/static/src/js/EvtcArea/**.js",

            # Appointment
            "evtc_front/static/src/js/EvtcAppointment/**.js",

            # Vehicle
            "evtc_front/static/src/js/EvtcVehicle/**.js",

            # Payment
            "evtc_front/static/src/js/EvtcPayment/**.js",

            # others js files
            "evtc_front/static/src/js/evtc_final_resume.js",
            "evtc_front/static/src/js/evtc.js",

            # plugin
            "evtc_front/static/src/js/plugins/jquery.timeselector.js",
            "evtc_front/static/src/js/library/html2canvas.js",

            # styles
            "evtc_front/static/src/scss/**.scss",
            "evtc_front/static/src/css/**.css",
            "evtc_front/static/src/js/plugins/jquery.timeselector.css",
        ],
        'web.assets_qweb': [
            'evtc_front/static/src/**/*.xml',
        ],
    }
}
