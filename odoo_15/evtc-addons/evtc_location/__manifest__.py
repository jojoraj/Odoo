{
    'name': "evtc location",
    'author': "A.Maximilien",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'evtc_front'],
    'data': [
        "views/others_information_partner_long_duration.xml",
        'views/long_duration.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            # google map
            "evtc_location/static/src/js/gmaps/map.js",
            "evtc_location/static/src/js/gmaps/_pins.js",
            "evtc_location/static/src/js/gmaps/_functions.js",
            "evtc_location/static/src/js/gmaps/_events.js",
            "evtc_location/static/src/js/gmaps/_my_device.js",
            "evtc_location/static/src/js/gmaps/_token_session.js",
            "evtc_location/static/src/js/gmaps/loaders.js",
            "evtc_location/static/src/js/gmaps/_extend_functions.js",
            "evtc_location/static/src/js/gmaps/session.js",
            "evtc_location/static/src/js/gmaps/PinsWithPrecision.js",
            "evtc_location/static/src/js/gmaps/getPlacePredictions.js",
            # others js files
            "evtc_location/static/src/js/plugins/jquery.timeselector.js",
            "evtc_location/static/src/js/library/html2canvas.js",
            # long duration js
            "evtc_location/static/src/js/long_duration/evtc_recuperation_long.js",
            "evtc_location/static/src/js/long_duration/evtc_vehicle_long.js",
            "evtc_location/static/src/js/long_duration/evtc_package_long.js",
            "evtc_location/static/src/js/long_duration/evtc_appointment_long.js",
            "evtc_location/static/src/js/long_duration/evtc_payment_resume_long.js",
            "evtc_location/static/src/js/long_duration/evtc_final_resume_long.js",

            # styles
            "evtc_location/static/src/scss/evtc.scss",
            "evtc_location/static/src/scss/marker.scss",
            "evtc_location/static/src/css/gmaps.css",
            "evtc_location/static/src/scss/loader.scss",
            "evtc_location/static/src/js/plugins/jquery.timeselector.css",
        ],
    }
}
