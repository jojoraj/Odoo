from odoo import api, fields, models


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    def redirect_to_survey(self):
        if self._context.get('redirect_manager'):
            return self.manager_survey_id.action_test_survey()
        if self._context.get('redirect_employee'):
            return self.employee_survey_id.action_test_survey()
        if self._context.get('redirect_collaborater'):
            return self.collaborators_survey_id.action_test_survey()
        if self._context.get('redirect_colleagues'):
            return self.colleagues_survey_id.action_test_survey()


