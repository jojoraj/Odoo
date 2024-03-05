from odoo import fields, models, api
from odoo.exceptions import UserError


class ProjectTaskNumber(models.Model):
    _inherit = "project.task"
    _description = "Task number"

    sequence_task = fields.Integer(string="Task Number sequence", default=0)

    @api.model
    def create(self, values):
        res = super(ProjectTaskNumber, self).create(values)

        if not self.env.context.get('from_duplicate'):
            if res.project_id:
                max_sequence = max(res.project_id.task_ids.mapped('sequence_task'), default=0)
                res.sequence_task = max_sequence + 1

        return res

    @api.constrains('project_id', 'sequence_task')
    def check_sequence_task(self):
        if not self.env.context.get('from_duplicate'):
            for line in self:
                if len(line.project_id.task_ids.filtered(
                        lambda x: x.id != line.id and x.sequence_task == line.sequence_task and line.sequence_task != 0).mapped(
                        'id')) > 0:
                    raise UserError("Le numéro du ticket existe déjà pour une autre tâche.")

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self = self.with_context(from_duplicate=True)

        return super(ProjectTaskNumber, self).copy(default)
