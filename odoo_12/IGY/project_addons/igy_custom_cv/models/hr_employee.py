from odoo import fields, models, api


class HrEmplyee(models.Model):
	_inherit = 'hr.employee'
	
	experience_ids = fields.One2many('hr.experience', 'link')
	education_ids = fields.One2many('hr.education', 'link')
	profil = fields.Html('Profil')

	def get_last_name(self):
		last_name = ''
		if self.name:
			name = self.name.split(' ')
			if len(name) > 1:
				last_name = ' '.join(name[1: 4])

		return last_name
