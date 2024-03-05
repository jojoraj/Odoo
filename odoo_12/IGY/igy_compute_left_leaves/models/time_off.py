from datetime import date
import calendar
from datetime import datetime
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    # time_off_left = fields.Char(string='Time off left')

    time_off_left = fields.Char(string='Congé restant', compute='timeoff_left')

    def timeoff_left(self):
        for rec in self:
            (begin_date_obj, end_date_obj) = self.get_date()
            allocation = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.id)])
            allocation = allocation.filtered(lambda x: x.holiday_status_id.name =='Congé payé') #atsoina le fonction lambda mretourner holiday =""
            employee_allocation = allocation.mapped('number_of_days_display') #listeny ho tableau ny vaeur an'i number of days dis

            day_off = self.env['hr.leave'].search([('employee_id', '=', rec.id), ('state', '=', 'validate')]) #condition dans la deuxieme parenthese
            day_off = day_off.filtered(lambda x: x.holiday_status_id.name =='Congé payé')
            employee_day_off = day_off.mapped('number_of_days_display')

            self.get_date()

            rec.time_off_left = str(sum(employee_allocation) - sum(employee_day_off)) + " Jours"

    def get_date(self):
        today = fields.Date.today()

        month_date = today.month
        year_date = today.year

        date_month_day = calendar.monthrange(year_date, month_date)

        # begin_day = date_month_day[0]
        end_day = date_month_day[1]

        begin_date = "%s-%s-%s" % ("01", month_date, year_date)
        end_date = "%s-%s-%s" % (end_day, month_date, year_date)

        begin_date_obj = datetime.strptime(begin_date, '%d-%m-%Y')
        end_date_obj = datetime.strptime(end_date, '%d-%m-%Y')

        return (begin_date_obj, end_date_obj)

