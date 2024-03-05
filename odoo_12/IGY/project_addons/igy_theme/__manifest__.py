# -*- coding: utf-8 -*-

{
    "name": "Thème de l'ERP Interne",
    "summary": "Thème de l'ERP Interne",
    "version": "0.1.0",
    "category": "Theme/Backend",
	"description": """
		Le thème de l'ERP interne d'INGENOSYA
    """,
	'images':[
        'images/screen.png'
	],
    "author": "Igy_theme",
    "license": "",
    "installable": True,
    "depends": [
        'web',
        'web_responsive',

    ],
    "data": [
        'views/assets.xml',
		'views/res_company_view.xml',
		'views/users.xml',
		#'views/web.xml',
    ],

}

