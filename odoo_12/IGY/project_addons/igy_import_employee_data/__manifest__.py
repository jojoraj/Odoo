{
    'name': 'Igy Import Data',
    'version': '12.0.0.0',
    'summary': '',
    'description': '',
    'category': '',
    'author': '',
    'website': '',
    'license': '',
    'depends': [
        'smile_impex', 'hr', 'igy_payroll'
    ],
    'data': [
        'data/ir_model_template.xml',
        'views/import_hr_employees.xml',
        'views/import_igy_payroll_views.xml',
        'views/import_history.xml'

    ],
    'installable': True,
    'auto_install': False
}