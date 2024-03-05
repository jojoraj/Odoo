# -*- coding: utf-8 -*-

from odoo import models
from datetime import date, timedelta, datetime
import calendar

class ReportAttendanceDaily(models.AbstractModel ):
    _name="report.igy_attendance_report.attendance_daily"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet('presence')

        # Set the width of name of employee
        sheet.set_column(1,1,36)

        # Add format to the workbook 
        title_date = workbook.add_format({'bold': True, 'font_size': 15})
        
        # Get the date of today
        today = datetime.today()
        date_today = datetime(today.year, today.month, today.day, 0, 0, 0, 0)

        # Print the title 
        sheet.write(2,2,date_today.strftime('Présence du %d/%m/%y'),title_date)


       
        # Print in out headers
        sheet.write(3, 2, 'IN')
        sheet.write(3, 3, 'OUT')
        sheet.write(3, 4, 'IN')
        sheet.write(3, 5, 'OUT')
        sheet.write(3, 6, 'TOTAL')


        # Get all active employees
        employees = self.env['hr.employee'].search([('active', '=', True),
        ('id','!=',1),
        ('id', '!=',204),
        ('id','!=',219)
        ])

        for employee_line, employe in enumerate(employees):
            # write employee name
            sheet.write(employee_line + 4, 1, employe.name)

            # get the total of employes_working_hours
            employees_working_hours_months = []

            

            # search for attendance of employee
            attendances = self.env['hr.attendance'].search(
                [('employee_id', '=', int(employe.id)), ('check_in', '>',date_today )])

            # sort attendance by date_checking
            attendances = sorted(attendances, key=lambda attendance: attendance.check_in)


            # if employee doesn ' t checked
            if len(attendances) < 1:
                sheet.write(employee_line+4,6,'0:00')

            # if employee checked only 2 times
            if len(attendances) == 1:
                sheet.write(employee_line + 4, 2,
                            (attendances[0].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                if attendances[0].check_out != False:
                    sheet.write(employee_line + 4, 5,
                                (attendances[0].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                # compute the worked hours
                worked_hours = str(timedelta(hours=attendances[0].worked_hours)).rsplit(':', 1)[0]

                # add the working hours to the list
                employees_working_hours_months.append(attendances[0].worked_hours)

                sheet.write(employee_line + 4, 6, worked_hours)

            # if employee checked 4 times
            if len(attendances) == 2:
                sheet.write(employee_line + 4, 2,
                            (attendances[0].check_in + timedelta(hours=3)).strftime(' %H:%M:%S'))
                
                if attendances[0].check_out !=False:
                    sheet.write(employee_line + 4, 3,
                                (attendances[0].check_out + timedelta(hours=3)).strftime(' %H:%M:%S'))

                sheet.write(employee_line + 4, 4,
                            (attendances[1].check_in + timedelta(hours=3)).strftime(' %H:%M:%S'))
                if attendances[1].check_out !=False:
                    sheet.write(employee_line + 4, 5,
                                (attendances[1].check_out + timedelta(hours=3)).strftime(' %H:%M:%S'))

                # compute worked hours for second attendance
                total_hours = attendances[0].worked_hours + attendances[1].worked_hours

                # transform the total working hour to string
                total_hours_str = str(timedelta(hours=total_hours)).rsplit(':', 1)[0]

                sheet.write(employee_line + 4, 6, total_hours_str)

                # add the working hours to the list
                employees_working_hours_months.append(total_hours)

            # if employee checked more than 4 times in a day    
            if len(attendances) > 2:
                sheet.write(employee_line + 4, 2,
                            (attendances[0].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                if attendances[0].check_out:
                    sheet.write(employee_line + 4, 3,
                                (attendances[0].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))
                sheet.write(employee_line + 4, 4,
                            (attendances[-1].check_in + timedelta(hours=3)).strftime('%H:%M:%S'))
                if attendances[-1].check_out:
                    sheet.write(employee_line + 4, 5,
                                (attendances[-1].check_out + timedelta(hours=3)).strftime('%H:%M:%S'))

                # Compute the total hours
                total_hours = attendances[0].worked_hours + attendances[-1].worked_hours

                total_hours_str = str(timedelta(hours=total_hours)).rsplit(':', 1)[0]

                sheet.write(employee_line + 4, 6, total_hours_str)
                # add the working hours to the list
                employees_working_hours_months.append(total_hours)

                # column_date += 5

            