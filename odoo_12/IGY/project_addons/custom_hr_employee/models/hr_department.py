from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    def action_open_request_leave_department(self):
        action = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').read()[0]
        action['context'] = {
            'search_default_approve': 1
        }
        action['domain'] = [('department_id', '=', self.id)]
        return action


