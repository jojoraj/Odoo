# -*- coding: utf-8 -*-

from odoo import fields,models
from datetime import date,timedelta
import calendar
class ReportForecast(models.AbstractModel):
    _name="report.igy_forecast_reports.forecast_report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self,workbook,data,lines):
        for obj in lines:
            format1 = workbook.add_format({'font_size': 14})
            sheet = workbook.add_worksheet('forecast')

            #Entetes
            sheet.write(0,0,'Nom employé')
            sheet.write(0,1,'Gestionnaire')
            sheet.write(0,2,'Compétences')
            

            
            #Compute working 
            employees = self.env['hr.employee'].search([
                ('active','=',True),
                ('department_id','not in',[
                    self.env.ref('ingenosya_timesheet_reminder.dep_dir').id,
                    self.env.ref('ingenosya_timesheet_reminder.dep_admin_financ').id,
                    self.env.ref('__export__.hr_department_9_0f6231d3').id,
                    self.env.ref('hr.dep_sales').id,
                    self.env.ref('__export__.hr_department_5_b812f5bc').id,
                    self.env.ref('__export__.hr_department_4_7d9384d6').id
                    ])
            ])
            
            employees = sorted(employees,key = lambda employee:  employee.department_id.name if employee.department_id.name  else '')
            
            forecast_hours_tab = []
            for line,employee in enumerate(employees):
                today = date.today()
                current_date = today
                forecast_hours_line = []
                for months in range(3):
                    
                    date_end = date(current_date.year,current_date.month,calendar.monthrange(current_date.year,current_date.month)[1])
                    date_start = date(current_date.year,current_date.month,1)
                    #Suppose that forecast is in hour
                    forecast_hour = sum(self.env['project.forecast'].search([
                    ('active', '=', True),
                    ('start_date', '>=', date_start),
                    ('end_date', '<=', date_end),
                    ('employee_id', '=', employee.id)]).mapped('resource_hours'))

                    #get the weekend of the month
                    weekends = self._compute_weekends_of_month(date_start,date_end)

                    #compute the holidays
                    holidays = self.env['public.holiday'].search([('date', '>=', fields.Date.to_string(date_start)), ('date', '<=', fields.Date.to_string(date_end))]).mapped('date')
                        

                    working_hours = (int(date_end.day) - weekends - len(holidays)  )* 8
                    #Compute free_day in hours
                    free_day = (working_hours - forecast_hour) / 8

                    sheet.write(0,months+3,f"Nombre jours libres: '{date_start.strftime('%B')}'")

                    if free_day < 0 :
                        free_day = 0
                    sheet.write(line+1,months+3,free_day)

                    forecast_hours_line.append(free_day)

                    current_date += timedelta(days=date_end.day)
                forecast_hours_tab.append(forecast_hours_line)
                
                employee_name = employee.name
                if bool(employee.parent_id):
                    parent_name = employee.parent_id.name
                else:
                    parent_name = ''
                sheet.write(line+1,0,employee_name)
                sheet.write(line+1,1,parent_name)

                skills = ""
                for indice,employee_skill in enumerate(employee.employee_skill_ids):
                    if employee_skill.skill_id:
                        skills+= employee_skill.skill_id.name+','
                skills = skills[0:-1]
            
                sheet.write(line+1,2,skills)
            
            #Compute total
            tab_somme = []
            for j in range(len(forecast_hours_tab[0])):
                somme = 0
                for i in range(len(forecast_hours_tab)):
                    somme+=forecast_hours_tab[i][j]
                tab_somme.append(somme)
            
            #Write in excel total
            sheet.write(len(employees)+1,0,'Total')
            for column in range(len(tab_somme)):
                sheet.write(len(employees)+1,column+3,tab_somme[column]) 


    def _compute_weekends_of_month(self,date_start_week,date_end_week):
        weekends = []
        while date_start_week != date_end_week+timedelta(days=1):
            if date_start_week.weekday() == 5 or date_start_week.weekday() == 6:
                weekends.append(date_start_week)
            date_start_week += timedelta(days=1)
        return len(weekends)