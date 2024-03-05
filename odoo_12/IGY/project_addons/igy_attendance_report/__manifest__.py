# -*- coding: utf-8 -*-

{
    'name': "igy_attendance_report",

    'summary': """
        Report for employee""",


    'author': "Brice - Ingenosya",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_attendance'],

    # always loaded
    'data': [
        'report/attendance_report.xml'

    ],
    # only loaded in demonstration mode
    'application':True,
    'installable': True
}