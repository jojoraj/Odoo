{
    'name': 'Payroll Inherit Igy',
    'version': '12.0.0.0',
    'summary': '',
    'description': 'This module inherit Payroll module for editing the Report',
    'category': 'Payroll',
    'author': 'Raharijaona Brice Ainarivony',
    'depends': ['hr_payroll'],
    'data': [
        'views/hr_salary_rule.xml',
        'views/hr_payslip.xml',
        'report/hr_payroll.xml'
    ],
    'installable': True,
    'auto_install': False,

}