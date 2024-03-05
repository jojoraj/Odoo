# -*- coding: utf-8 -*-
from typing import DefaultDict
from odoo import models,fields,api,_
import calendar

class Employee(models.Model):
    _inherit="hr.employee"

    pin = fields.Char()
    is_user = fields.Char(compute="_is_current_user")
    project_ids = fields.Many2many('project.project',relation='project_employee_rel',column1='project_id',column2='employee_id',string='Projects')

    matricule = fields.Char(string='Matricule')
    date_cin = fields.Date(string='Date')

    is_user = fields.Char(compute="_is_current_user")
    name_emp = fields.Char(string="Name")
    first_name = fields.Char(string="First Name")
    address_emp = fields.Char(string="Address")
    cin_at = fields.Char(string="At")
    ostie_card = fields.Char(string="N° ostie card")
    level_study = fields.Selection([
        ('bacc', _('BACC')),
        ('bacc1', _('BACC+1')),
        ('bacc2', _('BACC+2')),
        ('bacc3', _('BACC+3')),
        ('bacc4', _('BACC+4')),
        ('bacc5', _('BACC+5'))
    ], string=_("Level of study"), default="bacc")
    speciality = fields.Char(string="Speciality")
    last_diploma = fields.Selection([
        ('baccalaureat', _('BACCALAUREAT')),
        ('licence', _('LICENCE')),
        ('dts', _('DTS')),
        ('maitrise', _('MAITRISE')),
        ('master', _('MASTER')),
        ('doctorat', _('DOCTORAT'))
    ], string=_("Last diploma"), default="baccalaureat")
    name_husband = fields.Char(string="Husband/Wife's name")
    child_number = fields.Integer(string="Number of child")
    # child_list = fields.Text(string="List of Children")
    formation = fields.Html(string="Formation")
    # children_id = fields.Many2many("children")
    children_lines = fields.One2many('hr.employee.lines', 'child_id', string="Children")


    date_stage  = fields.Date(string= "Date de fin de stage")
    date_debut_stage = fields.Date(string="Date de debut de stage")
    # skype id
    skype_id = fields.Char(string="Skype ID")
    check_information_ids = fields.One2many('hr.check.information', 'employee_id', string=_("Check-in d'intégration"))

    @api.model
    def _is_current_user(self):
        user_id = int(self.user_id)
        if user_id == self.env.uid:
            self.is_user = "True"
        else:
            self.is_user = "False"

    @api.onchange('children_lines')
    def _add_children(self):
        self.child_number = len(self.children_lines)

    @api.model
    def _is_current_user(self):
        user_id = int(self.user_id)
        if user_id == self.env.uid:
            self.is_user = "True"
        else:
            self.is_user =  "False"

    is_stagiaire  = fields.Boolean(default=False)
    is_marketting  = fields.Boolean(default=False)
    consultant = fields.Boolean(default=False)

    perf_marketting = fields.Integer(default = 1)
    has_manager_role = fields.Char(compute='_has_manager_role')
    show_presence = fields.Char(compute='_has_presence_access')
    @api.model
    def _has_manager_role(self):
        if self.env.user.has_group('hr.group_hr_manager'):
            self.has_manager_role = 'True'
        else:
            self.has_manager_role = 'False'
    
    @api.depends('is_user', 'has_manager_role')
    def _has_presence_access(self):
        if self.is_user and self.has_manager_role:
            if self.is_user == 'False' or self.has_manager_role == 'True':
                self.show_presence = 'False'
            else:
                self.show_presence = 'True'

    is_DP = fields.Boolean(compute="_compute_is_DP",
                           default=lambda self: True if self.env.user.has_group('hr.igy_dp') else False)

    def _compute_is_DP(self):
        if self.env.user.has_group('hr.igy_dp'):
            self.is_DP = True
        else:
            self.is_DP = False

    is_RH = fields.Boolean(compute="_compute_is_RH",
                           default=lambda self: True if self.env.user.has_group('hr.group_hr_manager') else False)

    def _compute_is_RH(self):
        if self.env.user.has_group('hr.group_hr_manager'):
            self.is_RH = True
        else:
            self.is_RH = False
    def generate_check_information_data(self):
        for line in self:
            list(map(
                lambda data_check:
                self.env['hr.check.information'].create({
                    'name': self.env.ref('custom_hr_employee.' + data_check).id,
                    'date': fields.Date.today(),
                    "employee_id": line.id
                })
                if self.env.ref(
                    'custom_hr_employee.' + data_check, False) and self.env.ref(
                    'custom_hr_employee.' + data_check).id not in line.check_information_ids.mapped('name.id')
                else False,
                list(map(
                    lambda x:
                    "hr_information_theme" + str(x + 1), range(13)
                ))
            ))

