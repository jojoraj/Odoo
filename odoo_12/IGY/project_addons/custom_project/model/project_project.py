# -*- coding: utf-8 -*-

# from _typeshed import Self
import re
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectInherit(models.Model):
    _inherit = "project.project"

    @api.depends('timesheet_ids', 'timesheet_ids.employee_id.is_stagiaire', 'timesheet_ids.employee_id.date_stage',
                 'timesheet_ids.employee_id.job_id', 'timesheet_ids.employee_id.date_debut_stage')
    def _compute_finished(self):
        piloting = self.env['hr.job'].search([('name', 'ilike', 'Directeur de projets'), ('name', 'not ilike', 'stagiaire')]).mapped('id')
        piloting_intern = self.env['hr.job'].search([('name', 'ilike', 'Directeur de projets'), ('name', 'ilike', 'stagiaire')]).mapped('id')
        developer = self.env['hr.job'].search([('name', 'ilike', 'Développeur'), ('name', 'not ilike', 'stagiaire')]).mapped('id')
        developer_intern = self.env['hr.job'].search([('name', 'ilike', 'développeur'), ('name', 'ilike', 'stagiaire')]).mapped('id')
        tester = self.env['hr.job'].search([('name', 'ilike', 'Testeur'), ('name', 'not ilike', 'stagiaire')]).mapped('id')
        tester_intern = self.env['hr.job'].search([('name', 'ilike', 'Testeur'), ('name', 'ilike', 'stagiaire')]).mapped('id')
        design = self.env['hr.job'].search([('name', 'ilike', 'Design'), ('name', 'not ilike', 'stagiaire')]).mapped('id')
        design_intern = self.env['hr.job'].search([('name', 'ilike', 'Design'), ('name', 'ilike', 'stagiaire')]).mapped('id')
        engineering_developer = self.env['hr.job'].search([('name', 'ilike', "Ingénieur d'Etudes et de Développement"), ('name', 'not ilike', 'stagiaire')]).mapped('id')
        engineering_developer_intern = self.env['hr.job'].search([('name', 'ilike', "Ingénieur d'Etudes et de Développement"), ('name', 'ilike', 'stagiaire')]).mapped('id')

        for project in self:
            total_revue, total_non_revue = 0, 0

            pilotage_stagiaire, dev_stagiaire, design_stagiaire, testeur_stagiaire, autre_stagiaire  = 0, 0, 0, 0, 0
            pilotage_sans_stagiaire, autre_sans_stagiaire, dev_sans_stagiaire, design_sans_stagiaire, testeur_sans_stagiaire = 0, 0, 0, 0, 0

            for time in project.timesheet_ids:
                total_non_revue = total_non_revue + time.unit_amount
                employee_id = time.sudo().employee_id
                if employee_id.job_id:
                    if 'stagiaire' not in employee_id.job_id.name.lower():
                        if employee_id.job_id.id in piloting:
                            pilotage_sans_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in developer + engineering_developer:
                            dev_sans_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in design:
                            design_sans_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in tester:
                            testeur_sans_stagiaire += time.unit_amount
                        else:
                            autre_sans_stagiaire += time.unit_amount
                    else:
                        if employee_id.job_id.id in piloting_intern:
                            pilotage_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in developer_intern + engineering_developer_intern:
                            dev_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in design_intern:
                            design_stagiaire += time.unit_amount
                        elif employee_id.job_id.id in tester_intern:
                            testeur_stagiaire += time.unit_amount
                        else:
                            autre_stagiaire += time.unit_amount
                else:
                    #Si le job id n'est pas défini prendre autre_sans_stagiaire
                    autre_sans_stagiaire += time.unit_amount

                total_revue = total_revue + time.unit_amount

            project.total_stagiaire = (
                                        pilotage_stagiaire + dev_stagiaire + design_stagiaire + testeur_stagiaire + autre_stagiaire) / 8
            project.total_sans_stagiaire = (
                                            pilotage_sans_stagiaire + dev_sans_stagiaire + design_sans_stagiaire + testeur_sans_stagiaire + autre_sans_stagiaire) / 8

            project.finished_revue, project.finished_non_revue = round((total_revue / 8), 2), round(
                (total_non_revue / 8), 2)

            project.pilotage_stagiaire, project.dev_stagiaire, project.design_stagiaire, project.testeur_stagiaire, project.autre_stagiaire = pilotage_stagiaire / 8, dev_stagiaire / 8, design_stagiaire / 8, testeur_stagiaire / 8, autre_stagiaire / 8
            project.pilotage_sans_stagiaire, project.dev_sans_stagiaire, project.design_sans_stagiaire, project.testeur_sans_stagiaire, project.autre_sans_stagiaire = pilotage_sans_stagiaire / 8, dev_sans_stagiaire / 8, design_sans_stagiaire / 8, testeur_sans_stagiaire / 8, autre_sans_stagiaire / 8

    @api.depends('finished_revue', 'initial')
    def _compute_percentage_initial_finished(self):
        for project in self:
            try:
                project.percentage_initial_finished = (project.finished_revue / project.initial) * 100
            except ZeroDivisionError:
                project.percentage_initial_finished = 0

            percentage_not_finished_initial = 100 - project.percentage_initial_finished
            project.percentage_not_finished_initial = percentage_not_finished_initial if percentage_not_finished_initial > 0 else 0

    @api.depends('estimation', 'finished_revue')
    def _compute_percentage_finished(self):
        for projet in self:
            if float(projet.estimation) == 0.0:
                projet.percentage_finished = 0
                projet.percentage_not_finished = 100
            else:
                projet.percentage_finished = (projet.finished_revue / projet.estimation) * 100
                percentage_not_finished = 100 - projet.percentage_finished
                if percentage_not_finished < 0:
                    projet.percentage_not_finished = 0
                else:
                    projet.percentage_not_finished = percentage_not_finished

    def zero_avancement(self):
        projects = self.env['project.project'].search([])
        for project in projects:
            project.avancement = 0.0

    @api.depends('timesheet_ids', 'timesheet_ids.employee_id.is_stagiaire', 'timesheet_ids.employee_id.date_stage',
                 'timesheet_ids.employee_id.job_id', 'timesheet_ids.employee_id.date_debut_stage', 'estimation',
                 'avancement')
    def _compute_prevision(self):
        for project in self:
            if project.avancement == 0:
                project.percentage_previsionnel = 0
            else:
                if project.estimation == 0:
                    project.percentage_previsionnel = 0
                else:
                    result = 0
                    result_init = (10000 * project.finished_revue) / (project.estimation * project.avancement)
                    result = (1000 * project.finished_revue) / (project.estimation * project.avancement)
                    project.percentage_previsionnel = result

    avancement = fields.Float(default=0.0)
    percentage_previsionnel = fields.Float(default=0.0, string="Prévision", compute="_compute_prevision", store=True)
    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'project_id',
        string='Timeheets'
    )

    def send_reporting_dashboard(self):
        projects = self.env["project.project"].search([])
        non_revue = projects.filtered(lambda project: project.estimation == 0)
        report_1 = projects.filtered(lambda project: project.percentage_finished <= 80)
        report_2 = projects.filtered(
            lambda project: project.percentage_finished >= 81 and project.percentage_finished <= 100)
        report_3 = projects.filtered(
            lambda project: project.percentage_finished >= 101 and project.percentage_finished <= 150)
        report_4 = projects.filtered(lambda project: project.percentage_finished >= 151)
        body_html = f"""
        Bonjour, \n\n
        Pour cette semaine voici le reporting du tableau de bord de chaque pprojet.

        La liste des projets dont le budget revu n’est pas encore mentionné : ({len(non_revue)})\n
        """
        for pr in non_revue:
            body_html += f"    - {pr.name}  \n"
        body_html += f"\n Voici la liste  des projets dont le budget consommé est inférieur ou égale à  80% ({len(report_1)}): \n"
        for pr in report_1:
            body_html += f"    - {pr.name} ({pr.percentage_finished}%) \n"
        body_html += f"\n Voici la liste  des projets dont le budget consommé est entre 81% et 100% ({len(report_2)}):  \n"
        for pr in report_2:
            body_html += f"    - {pr.name} ({pr.percentage_finished}%) \n"
        body_html += f"\n Voici la liste  des projets dont le budget consommé est entre 101% et 150%  ({len(report_3)}):\n"
        for pr in report_3:
            body_html += f"    - {pr.name} ({pr.percentage_finished}%) \n"
        body_html += f"\n Voici la liste  des projets dont le budget consommé est strictement supérieur à 150% ({len(report_4)}): \n"
        for pr in report_4:
            body_html += f"    - {pr.name} ({pr.percentage_finished}%) \n"

        print(body_html)

    finished_revue = fields.Float(
        compute='_compute_finished',
        string="Feuille de temps revues(en jours)",
        store=False,
        tracking=True
    )
    finished_non_revue = fields.Float(
        compute='_compute_finished',
        string="Feuille de temps non-revues(en jours)",
        store=False,
        tracking=True
    )
    percentage_initial_finished = fields.Integer(
        compute='_compute_percentage_initial_finished',
        string="Statut (initial)",
        default=0,
        store=False
    )
    percentage_not_finished_initial = fields.Integer(
        compute='_compute_percentage_initial_finished',
        string="Reste à faire (initial)",
        default=0,
        store=False
    )
    percentage_finished = fields.Integer(
        compute='_compute_percentage_finished',
        string="Fini",
        default=0,
        store=False,
    )
    percentage_not_finished = fields.Integer(
        compute='_compute_percentage_finished',
        string="Reste à  faire",
        default=0,
        store=False,
    )
    pilotage_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    autre_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )

    dev_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    attach_ids = fields.Many2many('ir.attachment')
    design_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    testeur_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )

    autre_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )

    pilotage_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    dev_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    design_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    testeur_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )
    client_ids = fields.Many2many(
        'res.users',
        string="Utilisateurs externes"
    )
    initial = fields.Float(
        default=0,
        string="initial(Jours)",
        store=True
    )
    estimation = fields.Float(
        default=0,
        string="estimation(Jours)",
        store=True
    )
    stage = fields.Selection([
        ('non_demarre', 'Non démarré'),
        ('en_cours', 'En Cours'),
        ('termine', 'Términé')
    ],
        string='Etape du proejet',
        default='non_demarre',
        required=False
    )

    states = fields.Selection([
        ('done', 'En_cours'),
        ('blocked', 'Terminé'), ],
        string='Status du projet',
        default='done'
    )
    type = fields.Selection([
        ('forfait', 'Forfait'),
        ('mco', 'MCO'),
        ('regie', 'Régie'),
        ('credidant', 'Crédit temps'),
        ('tct', 'TCT')
    ],
        string='Type du projet',
        default='mco',
        required=False
    )

    total_sans_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )

    description_dashboard = fields.Text(string='Description on the dashboard')
    total_stagiaire = fields.Float(
        compute='_compute_finished',
        default=0,
        store=False,
    )

    description = fields.Text(string='Description')

    project_member_ids = fields.One2many(
        'project.member',
        'project_id',
        string="Project members",
    )

    project_client_ids = fields.One2many(
        'project.project.client',
        'project_id',
        string='Clients du projets'
    )
    # project.group_project_manager
    front_end_techonology_ids = fields.One2many(
        comodel_name='hr.skill',
        inverse_name='front_end_project_id',
        string="Front-end Technologies"
    )
    back_end_techonology_ids = fields.One2many(
        comodel_name='hr.skill',
        inverse_name='back_end_project_id',
        string="Back-end Technologies"
    )
    bdd_techonology_ids = fields.One2many(
        comodel_name='hr.skill',
        inverse_name='bdd_project_id',
        string="Database Technologies"
    )
    other_techonology_ids = fields.One2many(
        comodel_name='hr.skill',
        inverse_name='other_project_id',
        string="Other Technologies"
    )
    buddget_without_tester = fields.Float(
        compute='_compute_buddget_without_tester',
        string="Budget sans testeurs et Intégrateurs")

    percentage_buddget_without_tester = fields.Float(
        compute='_compute_buddget_without_tester',
        string=" ")

    @api.onchange('finished_revue', 'design_sans_stagiaire', 'testeur_sans_stagiaire', 'initial', 'estimation')
    @api.depends('finished_revue', 'design_sans_stagiaire', 'testeur_sans_stagiaire', 'initial', 'estimation')
    def _compute_buddget_without_tester(self):
        for line in self:
            line.buddget_without_tester = line.finished_revue - (line.design_sans_stagiaire + line.testeur_sans_stagiaire)
            line.percentage_buddget_without_tester = ((line.buddget_without_tester * 100) / line.estimation) if line.estimation > 0 else 1

    @api.constrains('project_member_ids')
    def check_all_project_member(self):
        for line in self:
            all_partner_project = line.message_partner_ids.mapped('user_ids.employee_ids')
            all_project_employee_res = line.project_member_ids.mapped('employee_id')
            for employee in all_project_employee_res:
                if employee not in all_partner_project:
                    raise ValidationError(
                        _("L'employée :  {} n'est pas encore abonnés à ce projet").format(employee.name))


class ProjectMember(models.Model):
    _name = 'project.member'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(string="Description")
    project_member_title_id = fields.Many2one('project.member.title', string='Title')
    project_member_type_id = fields.Many2one('project.team.type', string='Title')
    project_id = fields.Many2one('project.project', string='Projects')


class ProjectMemberTitle(models.Model):
    _name = 'project.member.title'
    name = fields.Char(string="Description")


class ProjectClient(models.Model):
    _name = 'project.project.client'

    client_id = fields.Many2one('project.client', String="Client")
    project_id = fields.Many2one('project.project', string='Projects')

    roll = fields.Char(string="Rôle du client")
    mail = fields.Char(string="mail")
    phone = fields.Char(string="Numéro de télephone")


class Skill(models.Model):
    _inherit = "hr.skill"
    bdd_project_id = fields.Many2one('project.project', string='Projects')
    other_project_id = fields.Many2one('project.project', string='Projects')
    front_end_project_id = fields.Many2one('project.project', string='Projects')
    back_end_project_id = fields.Many2one('project.project', string='Projects')


class Client(models.Model):
    _name = 'project.client'
    name = fields.Char(string="Nom du client")


class team(models.Model):
    _name = 'project.team.type'
    name = fields.Char(string="Nom du type")


class InheritProjectTask(models.Model):
    _inherit = 'project.task'

    description_without_tags = fields.Text(string=_("Description sans balise HTML"),
                                           compute="_get_description_without_tags")

    @api.onchange('description')
    def _get_description_without_tags(self):
        for line in self:
            line.description_without_tags = re.compile(r'<[^>]+>').sub('', line.description) if line.description else ''
