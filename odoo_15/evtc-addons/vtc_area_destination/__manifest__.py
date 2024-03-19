{
    'name': "evtc area destination",
    'summary': """
        Add many destination for evtc
    """,
    'author': "etech consulting",
    'website': "http://www.etechconsulting-mg.com",
    'category': 'evtc_front',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'web', 'evtc_front', 'etech_fleet', 'crm', 'evtc_crm', 'point_of_sale', 'esanandro_geotab'],
    'data': [
        'security/ir.model.access.csv',
        'views/destination_main_list.xml',
        'views/wait_time_view.xml',
        'views/evtc_crm.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            "vtc_area_destination/static/src/js/form/**.js",
            "vtc_area_destination/static/src/js/destination/**.js",
            "vtc_area_destination/static/src/scss/**.scss",
        ],
        'point_of_sale.assets': [
            "vtc_area_destination/static/src/js/pos_orders/**.js",
        ],
        'web.assets_qweb': [
            'vtc_area_destination/static/src/xml/**.xml',
        ],
    }
}
