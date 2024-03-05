from odoo import fields, models, api


class HrEducation(models.Model):
	_name = 'hr.education'
	_description = 'Education'
	_order = 'period'
	
	period = fields.Char('Période', required=True)
	speciality = fields.Char(string="Specialité")
	diplome = fields.Selection([
		('baccalaureate', 'Baccalauréat'),
		('licence', 'Licence'),
		('maitrise', 'Maitrise'),
		('master', 'Master'),
		('doctorat', 'Doctorat'),
		('certificat', 'Certificat')
	], string="Diplôme")
	university = fields.Char('Ecole/Université', required=True)
	link = fields.Many2one('hr.employee')
