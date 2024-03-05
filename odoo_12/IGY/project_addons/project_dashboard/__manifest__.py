# -*- coding: utf-8 -*-
{
    'name': 'Dashboard Project',
    'category': 'undefined',
    'description': """
        Un tableau de bord pour gérer le module projet.
    """,
    'depends': [
        'base',
        'project',
        'custom_project'
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/project_kanban_views.xml',
        'views/menu.xml',
        'views/project_view_filter.xml',
    ],
    'application' : True,
}