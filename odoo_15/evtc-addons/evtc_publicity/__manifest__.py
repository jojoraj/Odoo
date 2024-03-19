##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "evtc_publicity",
    'summary': """
        Manage everithing about publication on website E-vtc""",
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'website', 'rating'],
    'data': [
        'security/ir.model.access.csv',
        'views/evtc_pub_views.xml',
        'views/evtc_button_menu_views.xml',
        'views/snippets.xml',
        'views/modal.xml',
        'views/template_mail.xml',
        'views/ir_ui_menu.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            "evtc_publicity/static/src/js/app.js",
            "evtc_publicity/static/src/js/evtc_pub.js",
            "evtc_publicity/static/src/js/evtc_rating.js",
            "evtc_publicity/static/src/js/evtc_idea_box.js",
            "evtc_publicity/static/src/css/video.css",
            "evtc_publicity/static/src/css/icon.css",
            "evtc_publicity/static/src/css/star.css",
            "evtc_publicity/static/src/scss/evtc_pub.scss",
        ],
    },
}
