# -*- coding: UTF-8 -*-

import logging
from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def _alloc_monthly_leaves(self):
        # get type of leave to be allocated
        type_domain = [('is_current_year_type', '=', True)]
        leave_type_ids = self.env['hr.leave.type'].search(type_domain)
        if not leave_type_ids:
            _logger.info(_('No leave types found for automatic allocation'))
            return

        now = fields.Date.today()
        employee_tag_ids = self.env['hr.employee.category'].search([('allocation', '>', 0.00)])

        # admin, strange odoobot can't validate the leaves
        admin = self.env.ref('base.user_admin')

        for leave in leave_type_ids:
            for employee_tag in employee_tag_ids:
                values = {
                    'name': 'Allocation mensuelle %s %s' % (now.strftime('%B'), now.strftime('%Y')),
                    'holiday_status_id': leave.id,
                    'number_of_days': employee_tag.allocation,
                    'holiday_type': 'category',
                    'category_id': employee_tag.id,
                    'employee_id': False,  # to prevent the default method to be executed
                }
                try:
                    self.create(values).sudo(admin.id).action_approve()
                except Exception as e:
                    _logger.critical(e)
        return
