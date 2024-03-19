{
    'name': "Reset Password using SMS",
    'summary': """
    Reset password customization
""",
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Hidden/Tools',
    'version': '15.0.0.0.1',
    'license': 'AGPL-3',
    'depends': ['phone_validation', 'auth_signup', 'signup_validation_code'],
    'data': [
        'views/sms_fields.xml',
        'views/templates.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            'sms_password_reset/static/src/js/field_validation.js',
        ]
    },
    "external_dependencies": {
        "python": ['phonenumbers'],
    },
}
