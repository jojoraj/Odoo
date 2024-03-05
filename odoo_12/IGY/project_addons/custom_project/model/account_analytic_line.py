from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_last_three_month = fields.Date(string="Last 3 months")
    job_work_id = fields.Many2one('hr.job', string="Poste", related="employee_id.job_id", store=True)

    @api.constrains('project_id')
    def check_project_in_progress(self):
        for rec in self:
            if rec.project_id:
                if rec.project_id.stage == 'termine':
                    raise ValidationError("Vous ne pouvez pas insérer des feuilles de temps "
                                          "dans des projets terminer, pour plus d 'information,"
                                          " veuillez contacter votre responsable de projet " + rec.project_id.user_id.name+
                                          " ou votre Administrateur"
                                          )
