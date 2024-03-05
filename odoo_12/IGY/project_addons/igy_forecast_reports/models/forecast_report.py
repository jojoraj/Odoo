# -*- coding: UTF-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from calendar import monthrange as mr
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ForecastReport(models.TransientModel):
    _name = "forecast.report"
    _order = "sequence"

    sequence = fields.Integer()
    date_start = fields.Date()
    date_end = fields.Date()
    working_hours = fields.Float(compute="_compute_working_hours")
    forecast_hours = fields.Float(compute="_compute_forecast_hours")
    open_days = fields.Float(compute="_compute_open_days")
    company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.user.company_id)
    # can add employee later

    @api.depends("date_start", "date_end")
    def _compute_working_hours(self):
        # public holiday
        public_holiday_ids = self.env['public.holiday'].search([('date', '>=', fields.Date.to_string(self.date_start)), ('date', '<=', fields.Date.to_string(self.date_end))]).mapped('date')
        weekends = self._compute_weekends_of_month(self.date_start,self.date_end)
        employee_ids = self.env['hr.employee'].search([
                ('active','=',True),
                ('department_id','not in',[
                    self.env.ref('ingenosya_timesheet_reminder.dep_dir').id,
                    self.env.ref('ingenosya_timesheet_reminder.dep_admin_financ').id,
                    self.env.ref('__export__.hr_department_9_0f6231d3').id,
                    self.env.ref('hr.dep_sales').id,
                    self.env.ref('__export__.hr_department_5_b812f5bc').id,
                    self.env.ref('__export__.hr_department_4_7d9384d6').id
                    ])
            ]).ids
        self.working_hours = (self.date_end.day - len(public_holiday_ids) - weekends) * 8 * len(employee_ids)

    @api.depends("date_start", "date_end")
    def _compute_forecast_hours(self):
        employee_ids = self.env['hr.employee'].search([
                ('active','=',True),
                ('department_id','not in',[
                    self.env.ref('ingenosya_timesheet_reminder.dep_dir').id,
                    self.env.ref('ingenosya_timesheet_reminder.dep_admin_financ').id,
                    self.env.ref('__export__.hr_department_9_0f6231d3').id,
                    self.env.ref('hr.dep_sales').id,
                    self.env.ref('__export__.hr_department_5_b812f5bc').id,
                    self.env.ref('__export__.hr_department_4_7d9384d6').id
                    ])
            ]).ids
        forecast_hours = sum(self.env['project.forecast'].search([
            ('active', '=', True),
            ('start_date', '>=', self.date_start),
            ('end_date', '<=', self.date_end),
            ('employee_id', 'in', employee_ids)]).mapped('resource_time'))
        # supposed that forecast_uom is in hours
        self.forecast_hours = forecast_hours 

    @api.depends("working_hours", "forecast_hours")
    def _compute_open_days(self):
        self.open_days = (self.working_hours - self.forecast_hours) / 8

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        if self.date_start > self.date_end:
            ValidationError(_("the start date cannot be less than the end date"))

    @api.model
    def _send_report(self):
        # check if report exists
        template_id = self.env.ref('igy_forecast_reports.mail_template_timesheet_reminder')
        if not template_id:
            _logger.critical("No mail template found for forecast reports")
            return

        months = [0, 1, 2]
        today = date.today()
        forecast_reports_ids = []
        for i, value in enumerate(months):
            d = today + relativedelta(months=i)
            try:
                res = self.env['forecast.report'].create({
                    'sequence': i + 1,
                    'date_start': date(d.year, d.month, 1),
                    'date_end': date(d.year, d.month, mr(d.year, d.month)[1])
                })
                forecast_reports_ids.append(res)
            except Exception as e:
                _logger.critical(str(e))
                return

        context = {'forecasts': forecast_reports_ids}

        try:
            print('sending mail')
            template_id.with_context(context).send_mail(forecast_reports_ids[0].id,force_send=True)
        except Exception as e:
            _logger.critical(str(e))
        return
    
    @api.model
    def _compute_weekends_of_month(self,date_start_week,date_end_week):
        weekends = []
        while date_start_week != date_end_week+timedelta(days=1):
            if date_start_week.weekday() == 5 or date_start_week.weekday() == 6:
                weekends.append(date_start_week)
            date_start_week += timedelta(days=1)
        return len(weekends)
    
