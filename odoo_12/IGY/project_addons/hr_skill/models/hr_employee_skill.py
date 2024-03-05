# Copyright 2013 Savoir-faire Linux
# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError

class EmployeeSkill(models.Model):
    _name = 'hr.employee.skill'
    _description = 'HR Employee Skill'
    _rec_name = 'complete_name'

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    skill_id = fields.Many2one(
        string='Skill',
        comodel_name='hr.skill',
    )
    skill_ids = fields.Many2many('hr.skill','employee_skill_rel','employee_id','skill_id',string="Sous Competence")
    level = fields.Selection(
        string='Level',
        selection=[
            ('0','Debutant'),
            ('1', 'Junior'),
            ('2', 'Intermediate'),
            ('3', 'Senior'),
            ('4', 'Expert'),
        ],select=True
    )
    level_id  = fields.Integer(store=True, compute="_compute_level")
    active = fields.Boolean(string="Active", related='employee_id.active', store=True)

    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    _sql_constraints = [
        (
            'hr_employee_skill_uniq',
            'unique(employee_id, skill_id)',
            'This employee already has that skill!'
        ),
    ]

    @api.multi
    @api.depends('employee_id.name', 'skill_id.name', 'level')
    def _compute_complete_name(self):
        levels = dict(self._fields['level'].selection)
        for employee_skill in self:
            employee_skill.complete_name = _(
                '%(employee)s, %(skill)s (%(level)s)'
            ) % {
                'employee': employee_skill.employee_id.name,
                'skill': employee_skill.skill_id.name,
                'level': levels.get(employee_skill.level),
            }

    @api.multi
    @api.depends('level')
    def _compute_level(self):
        for skill in self :
            if skill.level == '0':
                raise ValidationError(_('La valeur du champs niveau ne doit pas être à 0 étoile.'))
            elif skill.level == '1':
                skill.level_id = 1
            elif skill.level == '2':
                skill.level_id = 2
            elif skill.level == '3':
                skill.level_id = 3
            elif skill.level == '4':
                skill.level_id = 4
            else :
                raise ValidationError(_('La valeur du champs niveau ne doit pas être à 0 étoile.'))

    @api.model
    def create(self, vals):
        if vals['level'] == False or vals['level'] == '0':
            raise ValidationError(_('La valeur du champs niveau ne doit pas être à 0 étoile.'))
        return super(EmployeeSkill, self).create(vals)