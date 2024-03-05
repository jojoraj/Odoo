# -*- coding: UTF-8 -*-

from odoo import models, api, fields, _

import datetime


class PublicHoliday(models.Model):
    _name = "public.holiday"

    name = fields.Char(string="Description", required=True, copy=False)
    date = fields.Date(string="Date", copy=False, required=True, index=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'public_holiday_id', string="Analytic Lines")
    # TODO full-day, half-day
    # TODO add computed year and month for grouping
    # TODO fill automatically the timesheet (internal project) when it is holiday public for all employees

    _sql_constraints = [(
        'date_unique',
        'unique(date)',
        'The date is already taken by another public holiday'
    )]

    @api.model
    def create(self, vals):
        rec = super(PublicHoliday, self).create(vals)
        holiday_projects = self.env['ir.config_parameter'].sudo().get_param('project_timesheet_holiday.leave_timesheet_project_id')
        holiday_tasks = self.env['project.task'].search([('name', '=', "Jour férié"), ('project_id', '=', int(holiday_projects))])
        if len(holiday_tasks) == 0:
            task = self.env['project.task'].sudo().create({
                'name': _("Jour férié"),
                'project_id': int(holiday_projects),
                'active': True, 
                'company_id': 1,
            })
        else:
            task = holiday_tasks[0]
        employee_ids = self.env['hr.employee'].search([('active', '=', True)])
        for employee in employee_ids:
            self.env['account.analytic.line'].sudo().create({
                'name': rec.name,
                'project_id': int(holiday_projects),
                'task_id': int(task.id),
                'unit_amount': 8,
                'user_id': employee.user_id.id,
                'date': vals["date"],
                'employee_id': employee.id,
                'public_holiday_id': rec.id,
            })
        return rec

    @api.multi
    def unlink(self):
        for rec in self:
            rev = self.env['account.analytic.line'].search([('public_holiday_id', '=', rec.id)]).unlink()
        
        return super(PublicHoliday, self).unlink()

    @api.model
    def update_account_analytic_line(self):
        public_holiday_ids = self.env['public.holiday'].search([]).filtered(lambda x: x.date.year == fields.Date.today().year)
        holiday_projects = self.env['ir.config_parameter'].sudo().get_param('project_timesheet_holiday.leave_timesheet_project_id')
        holiday_tasks = self.env['project.task'].search([('name', 'ilike', "Jour férié"), ('project_id', '=', int(holiday_projects))], limit=1)
        for public_holiday_id in public_holiday_ids:
            employee_active_ids = self.env['hr.employee'].search([]).filtered(lambda employee: not(self.env['account.analytic.line'].search([
                ('employee_id', '=', employee.id), ('date', '=', public_holiday_id.date)
            ])))

            for employee_id in employee_active_ids:
                account_analytic_line = self.env['account.analytic.line'].search([
                    ('employee_id', '=', employee_id.id),
                    ('public_holiday_id', '=', public_holiday_id.id)
                ], limit=1)
                if not account_analytic_line:
                    date = public_holiday_id.date.strftime('%Y-%m-%d')
                    project_id = holiday_tasks.project_id
                    user_id = employee_id.user_id.id if employee_id.user_id else 'null'
                    analytic_account_id = project_id.analytic_account_id
                    create_date = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    create_uid = self.env.user.id
                    company_id = self.env.user.company_id
                    self._cr.execute("""
                        INSERT INTO account_analytic_line(name, project_id, task_id, unit_amount, user_id, date, employee_id, public_holiday_id, amount, account_id, company_id, active, create_date, create_uid)
                        VALUES('%s', %s, %s, 8, %s, '%s', %s, %s, 0, %s, %s, true, '%s', %s)
                    """ % (public_holiday_id.name.replace("'", " "), project_id.id, holiday_tasks.id, user_id, date, employee_id.id, public_holiday_id.id, analytic_account_id.id, company_id.id, create_date, create_uid))

            employee_unactive_ids = self.env['hr.employee'].search([
                    ('active', '=', False)
            ])

            for employee_unactive_id in employee_unactive_ids:
                unactive_line = self.env['account.analytic.line'].search([
                    ('employee_id', '=', employee_unactive_id.id),
                    ('public_holiday_id', '=', public_holiday_id.id),
                    ('active', '=', True)
                ], limit=1)
                if unactive_line:
                    self._cr.execute("UPDATE account_analytic_line set active = false WHERE id=%s" % unactive_line.id)
            self._cr.commit()
