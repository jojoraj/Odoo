# -*- coding: utf-8 -*-
import logging
from odoo.tools.float_utils import float_round as round
from odoo import models, api, fields, _
from datetime import * 
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _get_open_dates(self, today, i):
        count = 1
        dates = []
        date = today
        while count <= i:
            date = date - relativedelta(days=1)
            if not date.strftime("%w") in ('0', '6'):
                count += 1
                dates.append(date)
        return dates

    @api.model
    def time_sheet_reminder(self):

        today = date.today()
        if today.weekday() == 5 or today.weekday() == 6:
            return
        public_holidays_ids = self.env['public.holiday'].search([])
        for holiday in public_holidays_ids:
            if holiday["date"] == today:
                return
        # TODO : build the template if can not find it
        template = self.env.ref('ingenosya_timesheet_reminder.mail_template_timesheet_reminder')
        if not template:
            _logger.critical(_('Could not find template for timesheet reminder'))
            return

        # get j-30 dates
        today = date.today()
        yesterday = date.today() - relativedelta(days=1)

        # open work days
        open_work_days = self._get_open_dates(today, 30)

        # we have started to complete the timesheets on 1st Sept. 2020
        open_work_days = list(filter(lambda x: x >= date(2020, 9, 1), open_work_days))

        # public holiday
        public_holiday_ids = self.env['public.holiday'].search([('date', '>=', fields.Date.to_string(min(open_work_days))), ('date', '<=', fields.Date.to_string(yesterday))]).mapped('date')

        # remove public_holidays from open_work_days
        open_work_days = list(set(open_work_days) - set(public_holiday_ids))

        # get the admin id
        employee_admin_id = self.env.ref('hr.employee_admin')
        # get the main company
        company_id = self.env.ref('base.main_company')
        # employees
        employee_ids = self.env['hr.employee'].search([
            ('active', '=', True),
            ('company_id', '=', company_id.id),
            ('id', '!=', employee_admin_id.id),
            ('consultant', '=', False)
        ])
        # odoobot
        odoo_bot = self.env.ref('base.user_root')

        # direction_departement
        dep_dir = self.env.ref('ingenosya_timesheet_reminder.dep_dir')
        # finance_administration
        dep_fi = self.env.ref('ingenosya_timesheet_reminder.dep_admin_financ')

        for employee in employee_ids:
         
            if employee.department_id.id == dep_dir.id or employee.department_id.id == dep_fi.id:
                continue

            missing_timesheet = []

            # TODO change this to contract date
            if employee.date_begin_work:
                begin_date = employee.date_begin_work
            else:
                begin_date = employee.create_date.date()

            open_work_days_filtered = list(filter(lambda x: x >= begin_date, open_work_days))

            for d in open_work_days_filtered:
                account_analytic_line = self.env['account.analytic.line'].search(
                    [('is_timesheet', '=', True), ('employee_id', '=', employee.id), ('date', '=', fields.Date.to_string(d))])
                hr_timesheet_hour_count = sum(account_analytic_line.mapped('unit_amount'))
                hr_timesheet_hour_count_round = round(hr_timesheet_hour_count, precision_rounding=0.01)
                if hr_timesheet_hour_count_round < employee.resource_calendar_id.hours_per_day:
                    missing_timesheet.append(d)

            context = {'date': sorted(missing_timesheet)}
            if missing_timesheet:
                if not employee.user_id:
                    _logger.warning(_('The employee %s is not related to any user'))
                else:
                    # Si 1 ou 2 jours manquent => envoi du rappel à l'employé
                    # Si 3 jours manquent => envoi du rappel à l'employé + en copie (absence@ingenosya.mg)
                    # Si 4 jours manquent => envoi du rappel à l'employé + en copie (absence@ingenosya.mg + gestionnaire de l'employé)
                    # Si 5 jours ou plus manquent => envoi du rappel à l'employé + en copie (absence@ingenosya.mg + gestionnaire de l'employé + pilotage@ingenosya.mg)
                    email_cc = []
                    len_miss = len(missing_timesheet)
                    if len_miss >= 3:
                        email_cc.append('absence@ingenosya.mg')
                    if len_miss >= 4:
                        email_cc.append(employee.parent_id.work_email)
                    if len_miss >= 5:
                        email_cc.append('pilotage@ingenosya.mg')

                    # coma separated mail
                    # prevent null,False,empty values
                    email_cc = ','.join(list(filter(None, email_cc)))
                    context.__setitem__('email_cc', email_cc)

                    # sending mail
                    try:
                        template.with_context(context).send_mail(employee.id, force_send=True)
                    except Exception as e:
                        _logger.critical(e)
                    # sending message
                    try:
                        channel_odoo_bot_users = '%s, %s' % (odoo_bot.name, employee.user_id.name)
                        channel_obj = self.env['mail.channel']
                        channel_id = channel_obj.search([('name', 'like', channel_odoo_bot_users)])
                        if not channel_id:
                            channel_id = channel_obj.create(
                                {
                                    'name': channel_odoo_bot_users,
                                    'email_send': False,
                                    'channel_type': 'chat',
                                    'public': 'private',
                                    'channel_partner_ids': [(4, odoo_bot.partner_id.id), (4, employee.user_id.partner_id.id)]
                                }
                            )

                        body_html = self.env['mail.template'].with_context(context)._render_template(template.body_html, 'hr.employee', employee.id)

                        channel_id.message_post(
                            subject="Timesheet reminder",
                            body=body_html,
                            message_type='comment',
                            subtype='mail.mt_comment',
                        )
                    except Exception as e:
                        _logger.critical(e)
        return
