from odoo import fields, models, api
from datetime import timedelta


class InheritMail(models.TransientModel):
	_inherit = 'mail.compose.message'

	mailing_cold_id = fields.Many2one('mail.mass_mailing_cold', store=True)
	crm_lead_id = fields.Many2one('crm.lead', string="Opportunité", store=True)
	crm_lead_ids = fields.Many2many('crm.lead', string="Opportunités", store=True)
	date = fields.Datetime(string="Date d'envoie", store=True)
	customer = fields.Char(related='crm_lead_id.partner_id.name', string='Client', store=True)
	bdr_user_id = fields.Char(related='crm_lead_id.bdr_user_id.name', string='BDR', store=True)
	sdr_user_id = fields.Char(related='crm_lead_id.sdr_user_id.name', string='SDR', store=True)
	crm_lead_type = fields.Selection(related='crm_lead_id.type', string='Types', store=True)
	mail_type = fields.Selection([('cold', 'Cold Mailing.'), ('cv', 'Envoi CV'),  ('none', 'Aucun')], string='Mail Type', store=True)

	@api.multi
	def send_mail(self, auto_commit=False):
		res = super(InheritMail, self).send_mail(auto_commit)
		if self.crm_lead_id:
			if self.model == 'crm.lead':
				datas = {
					'crm_lead_id': self.crm_lead_id.id,
					'date': self.date,
					'year' : self.date.strftime('%Y'),
					'month': self.date.strftime('%B'),
					'customer': self.customer,
					'bdr_user_id': self.bdr_user_id,
					'sdr_user_id': self.sdr_user_id,
					'crm_lead_type': self.crm_lead_type,
					'mail_type': self.mail_type
				}
				new_mail = self.env['crm.mail'].sudo().create(datas)
		if self.crm_lead_ids:
			for crm_lead in self.crm_lead_ids:
				datas = {
						'crm_lead_id': crm_lead.id,
						'date': self.date,
						'year' : self.date.strftime('%Y'),
						'month': self.date.strftime('%B'),
						'customer': crm_lead.partner_id.name,
						'bdr_user_id': crm_lead.bdr_user_id.name,
						'sdr_user_id': crm_lead.sdr_user_id.name,
						'crm_lead_type': crm_lead.type,
						'mail_type': self.mail_type
					}
				new_mail = self.env['crm.mail'].sudo().create(datas)
				if self.mail_type == 'cv':
					crm_lead.last_date_mailing_cv = fields.Datetime.now() + timedelta(hours=3)
				# 	self.update_cv_number(crm_lead)
		return res

	def update_cv_number(self, crm_lead):
		""" This function update create and update automatically the Index of CV: CV,CV-1,CV-2
			The minimal value of index is stored on igy_custom_crm.minimal_cv_tag_value configuration
			It is CV-9 by default
		"""
		tag_name = crm_lead.tag_ids.mapped('name')
		if len(tag_name) > 0:
			tag_name = tag_name[0]
			if '-' in tag_name:
				index = tag_name.split('-')
				if len(index) > 0:
					actual_index = int(index[1])
					next_index = actual_index + 1
					tag = self.env['crm.lead.tag'].search([
						('name', '=', 'CV-' + str(next_index))
					], limit=1)
					tag_id = tag.id if tag else self.env['crm.lead.tag'].create({
						'name': 'CV-' + str(next_index)
					}).id
					crm_lead.write({
						'tag_ids': [(6, 0, [tag_id])]
					})
			else:
				CrmLeadTag = self.env['crm.lead.tag']
				tag_name = 'CV-1'
				lead_tag_id = CrmLeadTag.search([('name', '=', tag_name)], limit=1)
				tag_id = lead_tag_id.id if lead_tag_id else CrmLeadTag.create({'name': tag_name}).id
				crm_lead.write({'tag_ids': [(6, 0, [tag_id])]})
		else:
			CrmLeadTag = self.env['crm.lead.tag']
			tag_name = 'CV-1'
			lead_tag_id = CrmLeadTag.search([('name', '=', tag_name)], limit=1)
			tag_id = lead_tag_id.id if lead_tag_id else CrmLeadTag.create({'name': tag_name}).id
			crm_lead.write({'tag_ids': [(6, 0, [tag_id])]})
