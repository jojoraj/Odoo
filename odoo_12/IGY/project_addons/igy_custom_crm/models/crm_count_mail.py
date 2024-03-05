from odoo import fields, models, api
from datetime import datetime,date

class CrmMail(models.Model):
	_name = 'crm.mail'
	_description = 'Email history'
	
	crm_lead_id = fields.Many2one('crm.lead', string="Opportunité", store=True)
	date = fields.Datetime(string="Date d'envoie", store=True, default=datetime.now(), readonly=True)
	month = fields.Char(string="Mois", store=True, default=datetime.now().strftime('%B'), readonly=True)
	year = fields.Char(string="Année", store=True, default=datetime.now().strftime('%Y'), readonly=True)
	customer = fields.Char(related='crm_lead_id.partner_id.name', string='Client', store=True)
	bdr_user_id = fields.Char(related='crm_lead_id.bdr_user_id.name', string='BDR', store=True)
	sdr_user_id = fields.Char(related='crm_lead_id.sdr_user_id.name', string='SDR', store=True)
	crm_lead_type = fields.Selection(related='crm_lead_id.type', string='Types', store=True)
	mail_type = fields.Selection([('cold', 'Cold Mailing.'), ('cv', 'Envoi CV'),  ('none', 'Aucun')], string='Mail Type')
