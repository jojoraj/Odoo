# -*- coding: utf-8 -*-
{
    'name': "Cholera Riposte",

    'summary': """
        Ajouter un individu ayant bénéficié de la chimioprophylaxie lors des ripostes""",

    'description': """
    """,

    'author': "eTech consulting",
    'website': "https://etechconsulting-mg.com/",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'covid_localisation'],

    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/cholera_riposte_view_form.xml',
        'views/res_partner_view_form.xml',
        'views/sanitary_training_view.xml',
        'views/water_source.xml'
    ],
    'demo': [
    ],
}
