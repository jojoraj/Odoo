# -*- coding: utf-8 -*-
{
	'name': "Curriculum Vitae",
	
	'summary': """
	 Curriculum Vitae Management """,
	
	
	
	'author': "O'Neal Rabelais Ingenosya",
	# for the full list
	'category': 'Human Resources',
	'version': '1.0.0',
	
	# any module necessary for this one to work correctly
	'depends': ['base', 'hr', 'igy_subskill'],
	
	# always loaded
	'data': [
		'security/ir.model.access.csv',
		'data/paperformat.xml',
		'views/hr_employee.xml',
		'views/hr_experience.xml',
		'report/employee_cv_report.xml',
	],
	'installable': True,
}
