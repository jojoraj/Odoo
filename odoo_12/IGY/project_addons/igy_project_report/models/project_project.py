
from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'
    @api.multi
    def generate_excel(self):
        self.env["project.report"].send_report()