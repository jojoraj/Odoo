# -*- coding: utf-8 -*-


from odoo import models
from datetime import date, timedelta, datetime
import calendar


class ReportAttendance(models.AbstractModel):
    _name = "report.igy_attendance_report.attendance_report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        format1 = workbook.add_format({'font_size': 14})
        sheet = workbook.add_worksheet('presence')

        # Print headers
        # sheet.write(0, 0, 'Presence des employees')

        # Get the date of months
        dates_of_month = self._get_date_of_month()

        # Print the dates in header
        column = 2
        for date_day in dates_of_month:
            month_year = str(date_day.day) + ' ' + date_day.strftime('%B')
            sheet.write(2, column, month_year)
            column += 5

        # Print in out headers
        case_number = 2
        for case in range(len(dates_of_month)):
            sheet.write(3, case_number, 'IN')
            sheet.write(3, case_number + 1, 'OUT')
            sheet.write(3, case_number + 2, 'IN')
            sheet.write(3, case_number + 3, 'OUT')
            sheet.write(3, case_number + 4, 'TOTAL')
            case_number += 5

        # Print the Total of hour of employee
        sheet.write(3, case_number, 'SOMME DES HEURES DE TRAVAIL')

        # Get all active employees
        employees = self.env['hr.employee'].search([('active', '=', True),
        ('id','!=',1),
        ('id', '!=',204),
        ('id','!=',219)
        ])

        for employee_line, employe in enumerate(employees):
            # write employee name
            sheet.write(employee_line + 4, 1, employe.name)
            # get the date of month
            dates = self._get_date_of_month()

            # get the total of employes_working_hours
            employees_working_hours_months = []

            column_date = 2
            for date_month in dates:
                # make date_month in datetime
                date_month_time = datetime(
                    date_month.year, date_month.month, date_month.day, 0, 0, 0, 0)

                # search for attendance of employee
                attendances = self.env['hr.attendance'].search(
                    [('employee_id', '=', int(employe.id)), ('check_in', '>', date_month_time),
                     ('check_out', '<', date_month_time + timedelta(days=1))])

                # sort attendance by date_checking
                attendances = sorted(attendances, key=lambda attendance: attendance.check_in)

                # print attendance of user

                # if employee doesn ' t checked
                if len(attendances) < 1:
                    pass

                # if employee checked only 2 times
                if len(attendances) == 1:
                    sheet.write(employee_line + 4, column_date,
                                (attendances[0].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 3,
                                (attendances[0].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                    # compute the worked hours
                    worked_hours = str(timedelta(hours=attendances[0].worked_hours)).rsplit(':', 1)[0]

                    # add the working hours to the list
                    employees_working_hours_months.append(attendances[0].worked_hours)

                    sheet.write(employee_line + 4, column_date + 4, worked_hours)

                # if employee checked 4 times
                if len(attendances) == 2:
                    sheet.write(employee_line + 4, column_date,
                                (attendances[0].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 1,
                                (attendances[0].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                    sheet.write(employee_line + 4, column_date + 2,
                                (attendances[1].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 3,
                                (attendances[1].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                    # compute worked hours for second attendance
                    total_hours = attendances[0].worked_hours + attendances[1].worked_hours

                    # transform the total working hour to string
                    total_hours_str = str(timedelta(hours=total_hours)).rsplit(':', 1)[0]

                    sheet.write(employee_line + 4, column_date + 4, total_hours_str)

                    # add the working hours to the list
                    employees_working_hours_months.append(total_hours)

                # if employee checked more than 4 times in a day    
                if len(attendances) > 2:
                    sheet.write(employee_line + 4, column_date,
                                (attendances[0].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 1,
                                (attendances[0].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 2,
                                (attendances[-1].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                    sheet.write(employee_line + 4, column_date + 3,
                                (attendances[-1].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                    # Compute the total hours
                    total_hours = attendances[0].worked_hours + attendances[-1].worked_hours

                    total_hours_str = str(timedelta(hours=total_hours)).rsplit(':', 1)[0]

                    sheet.write(employee_line + 4, column_date + 4, total_hours_str)
                    # add the working hours to the list
                    employees_working_hours_months.append(total_hours)

                column_date += 5

            # Compute the total hours of employees
            total_hours_employee = sum(employees_working_hours_months)

            # Convert float total to hours
            # Get the hours of time
            hours = int(total_hours_employee)

            # Get the minutes of hours
            minutes = int((total_hours_employee - hours) * 60)
            total_hours_str = "{}:{}".format(str(hours), str(minutes))
            sheet.write(employee_line + 4, column_date, total_hours_str)

    def _get_date_of_month(self):
        # get the current date
        current_date = date.today()

        # get the beginning of month
        beginning_date = date(current_date.year, current_date.month, 1)
        # get the end of month
        end_date = date(current_date.year, current_date.month, calendar.monthrange(
            current_date.year, current_date.month)[1])

        dates_of_month = []
        while beginning_date != (end_date + timedelta(days=1)):
            if beginning_date.weekday() != 5 and beginning_date.weekday() != 6:
                dates_of_month.append(beginning_date)
            beginning_date += timedelta(days=1)

        # Get all date from month
        return dates_of_month
