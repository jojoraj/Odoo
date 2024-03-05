from odoo import fields, models, api
import math


class CrmMAil(models.Model):
    _inherit = "crm.mail"

    partner_id = fields.Many2one("res.partner", related="crm_lead_id.partner_id", store=True)
    stage_id = fields.Many2one("crm.stage", string='Stage', related="crm_lead_id.stage_id", store=True)
    stage_two_id = fields.Many2one("crm.stage.two", string='Stage opportunité', related="crm_lead_id.stage_two_id", store=True)
    conversion_rate_cv = fields.Float(string="Taux de conversion envoi CV", store=True)
    conversion_rate_cold = fields.Float(string="Taux de conversion envoi Cold", store=True)
    conversion_total_rate_cv_cold = fields.Float(string="Taux de conversion envoi CV et Cold", store=True)
    active = fields.Boolean(string="Active", related="crm_lead_id.active", store=True) #Mail archivé avec les pistes
    last_stage_id = fields.Many2one('crm.stage', string='Dernière étape', related='crm_lead_id.last_stage_id', store=True)
    date_won = fields.Date(String="Date de réponse positive CV/Cold", related='crm_lead_id.date_won', store=True)
    positive_answer_cold_1st_sent = fields.Float(string="Reponse positif 1 er envoi", store=True)
    positive_answer_cold_2nd_sent = fields.Float(string="Reponse positif 2 ème envoi", store=True)
    positive_answer_cold_3rd_sent = fields.Float(string="Reponse positif 3 ème envoi", store=True)
    positive_answer_cold_4th_sent = fields.Float(string="Reponse positif 4 ème envoi", store=True)
    average_mail_sent_partner = fields.Integer(string="Moyenne mail envoyé par client", store=True)
    positive_answer_cold = fields.Integer(string="Réponse positive Cold", store=True)
    positive_answer_cv = fields.Integer(string="Réponse positive CV", store=True)
    total_positive_answer = fields.Integer(string="Total réponses positives", store=True)
    positive_answer_project_cv = fields.Integer(String="Nombre de projets CV gagné", store=True)
    positive_answer_project_cold = fields.Integer(String="Nombre de projets Cold gagné", store=True)
    total_positive_answer_project = fields.Integer(String="Total projet gagné", store=True)

    def compute_conversion_rate_cv(self):
        self.env.cr.execute("update crm_mail set conversion_rate_cv = 0 where conversion_rate_cv > 0;")
        self.env.cr.commit()
        total_mail_sent_cv = self.env['crm.mail'].search([('mail_type', '=', 'cv')])
        positive_answer_cv = len((self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive CV')])).mapped(id))
        self.conversion_rate_cv = positive_answer_cv / len(total_mail_sent_cv)

    def compute_conversion_rate_cold(self):
        self.env.cr.execute("update crm_mail set conversion_rate_cold = 0 where conversion_rate_cold > 0;")
        total_mail_cold = self.env['crm.mail'].search([('mail_type', '=', 'cold')])
        positive_answer_cold = len((self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])).mapped(id))
        self.conversion_rate_cold = positive_answer_cold / len(total_mail_cold)

    def compute_total_conversion_rate_cv_cold(self):
        self.env.cr.execute("update crm_mail set conversion_total_rate_cv_cold = 0 where conversion_total_rate_cv_cold > 0;")
        self.env.cr.commit()
        self.conversion_total_rate_cv_cold = self.conversion_rate_cv + self.conversion_rate_cold

    def compute_positive_answer_cold_1st_sent(self):
        self.env.cr.execute("update crm_mail set positive_answer_cold_1st_sent = 0 where positive_answer_cold_1st_sent > 0;")
        self.env.cr.commit()
        positive_answer_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])
        total_first_sent = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_first_send').id)])
        self.positive_answer_cold_1st_sent = (len(total_first_sent) / len(positive_answer_cold))
        self.positive_answer_cold_1st_sent = round(self.positive_answer_cold_1st_sent, 4)
        print('total positive answer', len(positive_answer_cold))
        print('first sent', len(total_first_sent))


    def compute_positive_answer_cold_2nd_sent(self):
        self.env.cr.execute("update crm_mail set positive_answer_cold_2nd_sent = 0 where positive_answer_cold_2nd_sent > 0;")
        self.env.cr.commit()
        positive_answer_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])
        total_second_sent = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                         ('mail_respond', '=', True),
                                                         ('stage_id', '=', self.env.ref('igy_custom_crm.igy_second_send').id)])
        self.positive_answer_cold_2nd_sent = (len(total_second_sent) / len(positive_answer_cold))

    def compute_positive_answer_cold_3rd_sent(self):
        self.env.cr.execute("update crm_mail set positive_answer_cold_3rd_sent = 0 where positive_answer_cold_3rd_sent > 0;")
        self.env.cr.commit()
        positive_answer_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])
        total_third_sent = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_third_send').id)])
        self.positive_answer_cold_3rd_sent = (len(total_third_sent) / len(positive_answer_cold))

    def compute_positive_answer_cold_4th_sent(self):
        self.env.cr.execute("update crm_mail set positive_answer_cold_4th_sent = 0 where positive_answer_cold_4th_sent > 0;")
        self.env.cr.commit()
        positive_answer_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])
        total_fourth_sent = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                         ('mail_respond', '=', True),
                                                         ('stage_id', '=', self.env.ref('igy_custom_crm.igy_fourth_send').id)])
        self.positive_answer_cold_4th_sent = (len(total_fourth_sent) / len(positive_answer_cold))

    def compute_average_mail_sent_partner(self):
        self.env.cr.execute("update crm_mail set average_mail_sent_partner = 0 where average_mail_sent_partner > 0;")
        self.env.cr.commit()

        total_mail_sent = self.env['crm.mail'].search([])

        self.env.cr.execute("select count(partners) as total from  (select count(partner_id) as partners from crm_mail group by partner_id )partners;")
        total_res_partner = self.env.cr.dictfetchone()['total']

        average_mail_sent_partner = len(total_mail_sent) / total_res_partner
        number_after_decimal = average_mail_sent_partner - int(average_mail_sent_partner)

        if number_after_decimal > 0.5:
            average_mail_sent_partner = math.ceil(average_mail_sent_partner)
        else:
            average_mail_sent_partner = math.floor(average_mail_sent_partner)

        if number_after_decimal > 0.5:
            average_mail_sent_partner = math.ceil(average_mail_sent_partner)
        else:
            average_mail_sent_partner = math.floor(average_mail_sent_partner)
        self.average_mail_sent_partner = average_mail_sent_partner

    def compute_positive_answer_cold(self):
        self.env.cr.execute("update crm_mail set positive_answer_cold = 0 where positive_answer_cold > 0;")
        self.env.cr.commit()
        positive_answer_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])
        positive_answer_cold = len(positive_answer_cold)
        print(positive_answer_cold)
        self.positive_answer_cold = positive_answer_cold

    def compute_positive_answer_cv(self):
        self.env.cr.execute("update crm_mail set positive_answer_cv = 0 where positive_answer_cv > 0;")
        self.env.cr.commit()
        positive_answer_cv = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive cv')])
        positive_answer_cv = len(positive_answer_cv)
        self.positive_answer_cv = positive_answer_cv

    def compute_total_positive_answer(self):
        self.env.cr.execute("update crm_mail set total_positive_answer = 0 where total_positive_answer > 0;")
        self.env.cr.commit()
        self.total_positive_answer = self.positive_answer_cv + self.positive_answer_cold

    def compute_positive_answer_project_cv(self):
        self.env.cr.execute("update crm_mail set positive_answer_project_cv = 0 where positive_answer_project_cv > 0;")
        self.env.cr.commit()
        positive_answer_project_cv = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive CV'), ('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id)])
        positive_answer_project_cv = len(positive_answer_project_cv)
        self.positive_answer_project_cv = positive_answer_project_cv

    def compute_positive_answer_project_cold(self):
        self.env.cr.execute("update crm_mail set positive_answer_project_cold = 0 where positive_answer_project_cold > 0;")
        self.env.cr.commit()
        positive_answer_project_cold = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'), ('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id)])
        positive_answer_project_cold = len(positive_answer_project_cold)
        self.positive_answer_project_cold = positive_answer_project_cold

    def compute_total_positive_answer_project(self):
        self.env.cr.execute("update crm_mail set total_positive_answer_project = 0 where total_positive_answer_project > 0;")
        self.env.cr.commit()
        total_positive_answer_project = self.positive_answer_project_cv + self.positive_answer_project_cold
        self.total_positive_answer_project = total_positive_answer_project

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmMAil, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        if view_type == 'dashboard':
            self.search([], limit=1).compute_conversion_rate_cv()
            self.search([], limit=1).compute_conversion_rate_cold()
            self.search([], limit=1).compute_total_conversion_rate_cv_cold()
            self.search([], limit=1).compute_positive_answer_cold_1st_sent()
            self.search([], limit=1).compute_positive_answer_cold_2nd_sent()
            self.search([], limit=1).compute_positive_answer_cold_3rd_sent()
            self.search([], limit=1).compute_positive_answer_cold_4th_sent()
            self.search([], limit=1).compute_average_mail_sent_partner()
            self.search([], limit=1).compute_positive_answer_cold()
            self.search([], limit=1).compute_positive_answer_cv()
            self.search([], limit=1).compute_total_positive_answer()
            self.search([], limit=1).compute_positive_answer_project_cv()
            self.search([], limit=1).compute_positive_answer_project_cold()
            self.search([], limit=1).compute_total_positive_answer_project()
        return res
