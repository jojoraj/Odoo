# -*- coding: UTF-8 -*-

from odoo import models, api, fields


class HrLeaveInherit(models.Model):
    _inherit = "hr.leave"

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        """ Change  value of days with holidays  """
        super(HrLeaveInherit, self)._onchange_leave_dates()
        if self.date_from and self.date_to:
            # Search for the holidays
            holidays = len(self.env['public.holiday'].search([('date', '<=', self.request_date_to), ('date', '>=', self.request_date_from)]))
            
            number_of_days = self.number_of_days - holidays
            if number_of_days < 0:
                self.number_of_days = 0
            else:
                self.number_of_days = number_of_days
    
    
    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):

        for holiday in self:    
            calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
            if holiday.date_from and holiday.date_to:
                # Search for the holiday
                holidays = len(self.env['public.holiday'].search([('date', '<=', holiday.request_date_to), ('date', '>=', holiday.request_date_from)]))

                # Get the number od hours
                number_of_hours = calendar.get_work_hours_count(holiday.date_from, holiday.date_to) - (holidays * 8)

                if number_of_hours < 0:
                    holiday.number_of_hours_display = 0
                
                else:
                    # Set the number of hours
                    holiday.number_of_hours_display = number_of_hours
