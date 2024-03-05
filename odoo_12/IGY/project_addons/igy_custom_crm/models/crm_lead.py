# -*- coding: utf-8 -*-

sub_state_proposal = [
            ('encryption', ('En cours de chiffrage')),
            ('writing', ('En cours de rédaction offre')),
            ('waiting', ('En attente de validation')),
            ('sent', ('Envoyée'))
        ]

import odoo
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class Crmlead(models.Model):
    _inherit = 'crm.lead'
    _description = 'Modification du module CRM '

    date_store = fields.Date(string='Date de prochaine envoi')

    crm_lead_cold_id = fields.Many2one('mail.mass_mailing_cold')

    crm_next_delivery_date = fields.Date(
        string="date prochaine envoie"
    )

    ao_week = fields.Char(
        string="Semaine AO"
    )
    ao_link = fields.Char(
        string="Lien"
    )
    ao_type = fields.Selection(
        selection=[('AO','AO'),
                   ('AMI','AMI')],
        string="AO type",
        default='AO'
    )
    contact = fields.Selection(
        selection=[('oui', 'Oui'),
                   ('non', 'Non')],
        string='Contacté par Ingenosya',
        required=True,
        default='non'
    )
    week_relaunch_date = fields.Date(
        string="Date de relance"
    )
    is_bdr = fields.Boolean(
        string="BDR crm",
        default=False
    )
    crm_type = fields.Selection(
        selection=[('local','Local'),
                   ('external','Externe')],
        string="Type de CRM",
        compute='_compute_crm_type',
        store=True,
        readonly=False
    )
    next_send_date = fields.Date(
        string="Prochaine date d'envoi",
    )
    check_origin_medium_date = fields.Date(
        string="Date pour la verification origine/medium",
        compute='compute_check_origin_medium_date'
    )
    contact_linkedin = fields.Date(string="Contacté linkedin COM")
    contact_phone = fields.Date(string="Contacté phoning COM")
    contact_mail = fields.Date(string="Contacté mailing COM")
    created_date = fields.Date(
        string='Créé le'
    )
    verif_nom = fields.Boolean(string="Nom verifié" , default=False)
    is_tender = fields.Boolean(
        string="Appel d'offre",
        default=False
    )
    week = fields.Char(
        string="Semaine",
        compute='compute_week'
    )
    sdr_user = fields.Selection(
        selection=[('sdra', 'SDRA'),
                   ('sdrb', 'SDRB')],
        string="SDR type"
    )
    type = fields.Selection(
        selection_add=[('global','Global')]
    )
    sub_state_proposal = fields.Selection(
        sub_state_proposal, string='Sous étapes propositions', default='encryption'
    )

    user_id = fields.Many2one(
        'res.users', string='Salesperson'
    )
    last_mass_mailing_id = fields.Many2one('mail.mass_mailing', string="Dernier origine du mailing")

    last_stage_id = fields.Many2one('crm.stage', string='Dernière étape', store=True)

    date_won = fields.Date(string="Date de réponse positive CV/Cold")


    def send_mail_crm(self):
        """
			This function opens a window to compose an email
        """
        print(self.env.ref('igy_custom_crm.group_admin_crm').mapped('users'))
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('igy_custom_crm', 'email_template_send')[0]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('igy_custom_crm', 'igy_crm_mail_compose_form_view')[1]
        except ValueError:
            compose_form_id = False
    
        ctx = dict(self.env.context or {})
        ctx.update(
            {
                'default_model': 'crm.lead',
                'active_model': 'crm.lead',
                'active_id': self.ids[0],
                'default_res_id': self.ids[0],
                'default_crm_lead_id': self.id,
                'default_date': datetime.now(),
                'default_partner_ids': [(4, self.partner_id.id)],
                'default_cc_recipient_ids': [(6,0,self.env.ref('igy_custom_crm.group_admin_crm').mapped('users.partner_id').mapped('id'))],
                'default_composition_mode': 'comment',
                'force_email': True,
                'mark_rfq_as_sent': True,
                'model_description': ('Envoie mail')
            }
        )
    
        return {
            'name': ('Envoie mail'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    count_mail = fields.Integer(readonly=True, compute='_count_mail')
    total_mail_count = fields.Integer(
        string="Total des email",
        compute='compute_total_mail_count',
        store=True
    )
    total_mail_lead = fields.Integer(
        string="Total des email",
        compute='compute_total_mail_lead',
        store=True
    )
    total_mail_oppor = fields.Integer(
        string="Total des email",
        compute='compute_total_mail_oppor',
        store=True
    )
    crm_mail_ids = fields.One2many(
        comodel_name='crm.mail',
        inverse_name='crm_lead_id',
        string="Les mails"
    )
    crm_mail_len = fields.Integer(
        string="Longueur mails",
        compute='compute_crm_mail_len',
        store=True
    )
    partner_name_child = fields.Char(string='Partner Name', compute='_compute_partner_name_child', store=False)

    last_date_update_tag = fields.Datetime(string="Date de dernière mise à jour des étiquettes")
    last_tag_update_user_id = fields.Many2one('res.users', string="Dernier utilisateur qui a mis a jour les étiquettes")
    last_date_update_stage = fields.Datetime(string="Date de derniere mise a jour des étapes")
    last_stage_update_user_id = fields.Many2one('res.users', string="Dernier utilisateur qui a mis a jour les étapes")
    last_date_mailing_cv = fields.Datetime(string="Date dernier mail Envoi CV")

    @api.onchange('crm_mail_ids')
    @api.depends('crm_mail_ids')
    def compute_crm_mail_len(self):
        for rec in self:
            if rec.crm_mail_ids:
                rec.crm_mail_len = len(rec.crm_mail_ids)

    @api.depends('crm_mail_ids')
    def compute_total_mail_lead(self):
        for rec in self:
            rec.total_mail_lead = self.env['crm.mail'].search_count([('crm_lead_type','=','lead')])

    @api.depends('crm_mail_ids')
    def compute_total_mail_oppor(self):
        for rec in self:
            rec.total_mail_oppor = self.env['crm.mail'].search_count([('crm_lead_type', '=', 'opportunity')])

    @api.depends('crm_mail_ids')
    def compute_total_mail_count(self):
        for rec in self:
            rec.total_mail_count = self.env['crm.mail'].search_count([])

    def _count_mail(self):
        for rec in self:
            rec.count_mail = len(self.env['crm.mail'].search([('crm_lead_id', '=', rec.id)]).mapped('id'))

    def open_crm_mail(self):
        return {
            'name': 'Historiques des emails',
            'domain': [('crm_lead_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'crm.mail',
            'view_id': False,
            'views': [(self.env.ref('igy_custom_crm.crm_mail_tree_view').id, 'tree')],
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'context': {
                "default_crm_lead_id": self.id,
            },
        }

    def button_to_writing(self):
        self.sub_state_proposal = 'writing'

    def button_to_waiting(self):
        self.sub_state_proposal = 'waiting'

    def button_to_sent(self):
        self.sub_state_proposal = 'sent'
        self.stage_two_id = self.env.ref('igy_custom_crm.bdr_crm_offer_sent')
        send = self.send_mail_crm()
        return send
        
    
    global_stage_id = fields.Many2one(
        comodel_name='crm.global.stage',
        string="Global stage",
        ondelete='restrict',
        track_visibility='onchange',
        index=True,
        copy=False,
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]",
        group_expand='_read_group_global_stage'
    )
    
    partner_address_mobile = fields.Char('Contact du partenaire', related='partner_id.mobile', readonly=True)


    @api.depends('created_date')
    def compute_check_origin_medium_date(self):
        for rec in self:
            if rec.created_date:
                rec.check_origin_medium_date = rec.created_date + relativedelta(months=1)


    @api.depends('created_date')
    def compute_week(self):
        for rec in self:
            if rec.created_date:
                rec.week = rec.created_date.isocalendar()[1]

    @api.depends('partner_id')
    def _compute_crm_type(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.country_id.id == self.env.ref('base.mg').id:
                    rec.crm_type = 'local'
                else:
                    rec.crm_type = 'external'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        elt = self.env['crm.stage'].search([])
        return elt

    @api.model 
    def _read_group_stage_two(self, stages, domain, order): 
        elt = self.env['crm.stage.two'].search([])
        return elt

    @api.model
    def _read_group_global_stage(self, stages, domain, order):
        GlobalStage = self.env['crm.global.stage'].search([])
        return GlobalStage

    def get_bdr_domain(self):
        users = self.env.ref('igy_custom_crm.group_crm_bdr').users.ids
        return [('id', 'in', users)]

    def get_sdr_domain(self):
        users = self.env.ref('igy_custom_crm.group_crm_sdr').users.ids
        return [('id', 'in', users)]

    def get_iav_domain(self):
        users = self.env.ref('igy_custom_crm.group_crm_iav').users.ids
        return [('id', 'in', users)]

    sdr_user_id = fields.Many2one('res.users', string='SDR', domain=get_sdr_domain)
    bdr_user_id = fields.Many2one('res.users', string='BDR', domain=get_bdr_domain)
    iav_user_id = fields.Many2one('res.users', string='IAV', domain=get_iav_domain)

    @api.multi
    def set_won_opportunity(self):
        for rec in self:
            rec.stage_two_id = self.env.ref('igy_custom_crm.bdr_crm_won').id

    @api.multi
    def set_proposition_opportunity(self):
        for rec in self:
            rec.stage_two_id = self.env.ref('igy_custom_crm.bdr_crm_proposition').id

    @api.multi
    def set_unqualified_opportunity(self):
        for rec in self:
            rec.stage_two_id = self.env.ref('igy_custom_crm.bdr_crm_lost').id

    @api.multi
    def set_won_lead(self):
        for rec in self:
            rec.stage_id = self.env.ref('igy_custom_crm.igy_crm_won').id

    @api.multi
    def set_unqualified_lead(self):
        for rec in self:
            rec.stage_id = self.env.ref('igy_custom_crm.igy_crm_unqalified').id

    @api.multi
    def write(self,values):
        stage_id = self.env["crm.stage"].search([('id','=',values.get('stage_id'))],limit=1)
        stage_two_id = self.env["crm.stage.two"].search([('id','=',values.get('stage_two_id'))],limit=1)
        for rec in self:
            if rec.stage_id.sequence < stage_id.sequence:
                if stage_id.id not in [self.env.ref('igy_custom_crm.igy_crm_fail').id,
                                       self.env.ref('igy_custom_crm.igy_crm_unqalified').id,
                                       self.env.ref('igy_custom_crm.igy_crm_won').id]:
                    if rec.write_date:
                        rec.next_send_date = datetime.date(rec.write_date) + timedelta(7)
            if rec.stage_two_id.sequence > stage_two_id.sequence:
                if stage_two_id.id in [self.env.ref('igy_custom_crm.bdr_crm_qualif').id]:
                    rec.next_send_date = datetime.date(rec.write_date) + timedelta(7)

            if stage_id.id == self.env.ref('igy_custom_crm.igy_crm_won').id:
                rec.date_won = fields.Date.today()
                rec.last_stage_id = rec.stage_id.id
                rec.type = 'opportunity'
                rec.stage_two_id = self.env.ref('igy_custom_crm.bdr_crm_qualif').id
                rec.is_bdr = True

        # if self.is_tender == False or values.get('is_tender') == False:
        #     if values.get("stage_two_id") in [self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id, self.env.ref('igy_custom_crm.bdr_crm_won').id]:
        #         if self.sub_state_proposal != 'sent':
        #             raise UserError(_('Operation interdite! Veuillez mettre le statut de la proposition comme envoyé!'))

        # Update relaunch date through the state changement
        if values.get("stage_two_id") == self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id:
            values['week_relaunch_date'] = datetime.today() + relativedelta(days=14)         # TODO update relaunch date if it has one relaunch

        # Update the values of users and date
        if values.get('stage_id'):
            values['last_date_update_stage'] = fields.Datetime.now() + timedelta(hours=3)
            values['last_stage_update_user_id'] = self.env.user.id

        if values.get('tag_ids'):
            values['last_date_update_tag'] = fields.Datetime.now() + timedelta(hours=3)
            values['last_tag_update_user_id'] = self.env.user.id
        res = super(Crmlead, self).write(values)
        return res

    @api.model
    def create(self, values):
        res = super(Crmlead, self).create(values)
        if res.create_date:
            res.next_send_date = datetime.date(res.create_date) + timedelta(7)
        return res

    stage_two_id = fields.Many2one('crm.stage.two', string='Stage', ondelete='restrict', track_visibility='onchange', index=True, copy=False,
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]",
        group_expand='_read_group_stage_two')

    def send_mail_change_state(self, stage_ids, users):
        crm_lead_res = self.sudo().search([])
        crm_lead_filtered = crm_lead_res.filtered(
            lambda x: x.stage_id.id in stage_ids
        )
        user_tab = []
        for user in users:
            user_tab.append(user)
            crm_tab = []
            for crm_lead in crm_lead_filtered:
                if crm_lead.next_send_date:
                    if crm_lead.next_send_date <= datetime.today().date():
                        crm_tab.append(crm_lead)
            if len(crm_tab) > 0:
                template_id = self.env.ref('igy_custom_crm.crm_change_stage_mail_template', raise_if_not_found=False)
                crm_lead_obj = crm_lead_filtered[0]
                template_id.with_context(crm_lead=crm_tab, user=user).send_mail(
                    crm_lead_obj.id, force_send=True)

    @api.model
    def check_crm_next_call_day(self):
        sdr_stage_ids = [self.env.ref('igy_custom_crm.igy_qualification_marketting').id,
                 self.env.ref('igy_custom_crm.igy_first_send').id,
                 self.env.ref('igy_custom_crm.igy_second_send').id,
                 self.env.ref('igy_custom_crm.igy_third_send').id]
        sdr_users = self.env.ref('igy_custom_crm.group_crm_sdr').mapped('users')
        self.send_mail_change_state(stage_ids=sdr_stage_ids, users=sdr_users)

    def send_mail_for_origin_medium(self, users):
        crm_lead_res = self.sudo().search(
            [('is_bdr','=',True),
             ('stage_two_id','not in', [self.env.ref('igy_custom_crm.igy_crm_fail').id,
                                        self.env.ref('igy_custom_crm.igy_crm_unqalified').id])]
        )
        crm_lead_filtered = crm_lead_res.filtered(
            lambda x: x.source_id.id == self.env.ref('igy_custom_crm.utm_source_on_demand').id or x.medium_id.id == self.env.ref('igy_custom_crm.utm_medium_on_demand').id)
        user_tab = []
        for user in users:
            user_tab.append(user)
            crm_tab = []
            for crm_lead in crm_lead_filtered:
                if crm_lead.check_origin_medium_date:
                    if crm_lead.check_origin_medium_date == datetime.today().date():
                        crm_tab.append(crm_lead)
            if len(crm_tab) > 0:
                template_id = self.env.ref('igy_custom_crm.crm_change_origin_medium_mail_template', raise_if_not_found=False)
                crm_lead_obj = crm_lead_filtered[0]
                template_id.with_context(crm_lead=crm_tab, user=user).send_mail(
                    crm_lead_obj.id, force_send=True)

    def send_mail_relaunch(self, users):
        crm_lead_res = self.sudo().search(
            [('is_bdr', '=', True),
             ('stage_two_id', 'in', [self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id])]
        )
        crm_lead_filtered = crm_lead_res.filtered(
            lambda x: x.week_relaunch_date == datetime.today().date())
        user_tab = []
        for user in users:
            user_tab.append(user)
            crm_tab = []
            for crm_lead in crm_lead_filtered:
                crm_tab.append(crm_lead)
            if len(crm_tab) > 0:
                template_id = self.env.ref('igy_custom_crm.crm_lead_relaunch_mail_template',
                                           raise_if_not_found=False)
                crm_lead_obj = crm_lead_filtered[0]
                template_id.with_context(crm_lead=crm_tab, user=user).send_mail(
                    crm_lead_obj.id, force_send=True)

    @api.model
    def relaunch_offer_sent(self):
        bdr_users = self.env.ref('igy_custom_crm.group_crm_bdr').mapped('users') # TODO change this to the bdr user only
        self.send_mail_relaunch(bdr_users)


    @api.model
    def check_origin_medium_utm(self):
        bdr_users = self.env.ref('igy_custom_crm.group_crm_bdr').mapped('users')
        self.send_mail_for_origin_medium(bdr_users)

    @api.model
    def default_get(self, fields):
        """
		Definition or rules to manage roles access
		:param fields:
		:return:
		"""
        res = super(Crmlead, self).default_get(fields)
        self = self.sudo()
        allowed_users_ids = []
        admin_users_ids = self.env.ref('igy_custom_crm.group_admin_crm').mapped('users').mapped('id')
        allowed_users_ids = admin_users_ids
        allowed_users_ids = list(dict.fromkeys(allowed_users_ids))
        res['admin_crm_ids'] = [(6, 0, allowed_users_ids)]
        return res

    admin_crm_ids = fields.Many2many(
        'res.users', 'admin_crm_id_rel', string='Abonnés'
    )


    @api.multi
    def back_sub_stage(self):

        for rec in self:
            actual_index = rec.get_sub_state_index(rec.sub_state_proposal)
            rec.sub_state_proposal = rec.get_old_index(actual_index)
            pass

    def get_sub_state_index(self, actual_sub_state):
        i = 0
        for sub_state in sub_state_proposal:
            if sub_state[0] == actual_sub_state:
                return i
            i +=1

    def get_old_index(self, index):
        return sub_state_proposal[index-1][0]

    def process_update_tag(self):
        """Method to render multiple update lead tags form"""
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.tag',
            'target': 'new',
            'context': {'default_lead_ids': [(6, 0, self.mapped('id'))]}
        }

    def process_update_stage(self):
        """Method to render multiple update lead stage form"""
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.stage',
            'target': 'new',
            'context': {'default_lead_ids': [(6, 0, self.mapped('id'))]}
        }

    def _compute_partner_name_child(self):
        for rec in self:
            rec.partner_name_child = ' '
            if rec.partner_id:
                if rec.partner_id.child_ids and len(rec.partner_id.child_ids) > 0:
                    rec.partner_name_child = rec.partner_id.child_ids[0].name
                    rec.partner_name_child += rec.partner_id.child_ids[0].firstname if rec.partner_id.child_ids[0].firstname else ''
                    rec.partner_name_child += ' '+ rec.partner_id.child_ids[0].firstname if rec.partner_id.child_ids[0].firstname else ''
