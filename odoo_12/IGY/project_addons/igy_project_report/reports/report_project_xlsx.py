# -*- coding: utf-8 -*-

from odoo import fields,models
from datetime import date,timedelta
import calendar
class ReportProject(models.AbstractModel):
    _name="report.igy_project_report.project_report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self,workbook,data,lines):
        for obj in lines:
            projects = self.env["project.project"].search([])
            projects = projects.filtered(lambda project : project.stage  == 'en_cours' and project.type == 'forfait')
            titre = workbook.add_format({'font_size': 14,'bold': True})
            entete = workbook.add_format({'font_size': 11,'bold': True})

            #Budget estimer non rensigner
            sheet1 = workbook.add_worksheet('Budget revu = 0')
            sheet1.write(0,0,'Budget revu non-renseigné',titre)
            sheet1.write(2,1,'Nom du projet',entete)
            non_revue = projects.filtered(lambda project: project.estimation == 0 )
            print(
                """
                >>>>
                >>>>
                >>>>
                """
            )
            for i,value  in enumerate(non_revue) :
                i += 3
                sheet1.write(i, 1, value.name)
                i += 1

            #Budget estimer non rensigner
            sheet6 = workbook.add_worksheet('Avancement du projet = 0')
            sheet6.write(0,0,"L'avancement du projet est non estimé",titre)
            sheet6.write(2,1,'Nom du projet',entete)
            non_avancement = projects.filtered(lambda project: project.avancement == 0 )
            for i,value  in enumerate(non_avancement) :
                i += 3
                print(i,value)
                sheet6.write(i, 1, value.name)
                i += 1

            #Budget consommé est inférieur à 80%
            sheet2 = workbook.add_worksheet('Budget 0-80%')
            sheet2.write(0,0,'Budget consommé entre 0-80%',titre)
            sheet2.write(2,1,'Nom du projet',entete)
            sheet2.write(2,2,'Budget consommé',entete)
            report_1 = projects.filtered(lambda project: project.percentage_finished <= 80)
            for i,value  in enumerate(report_1) :
                i += 3
                sheet2.write(i, 1, value.name)
                sheet2.write(i, 2, f"{value.percentage_finished}%")
                i += 1         


            #Budget consommé est entre 81 - 100 %
            sheet3 = workbook.add_worksheet('Budget 81-100%')
            sheet3.write(0,0,'Budget consommé entre 81-100%',titre)
            sheet3.write(2,1,'Nom du projet',entete)
            sheet3.write(2,2,'Budget consommé',entete)
            report_2 = projects.filtered(lambda project: project.percentage_finished >= 81 and project.percentage_finished <= 100 )
            for i,value  in enumerate(report_2) :
                i += 3
                sheet3.write(i, 1, value.name)
                sheet3.write(i, 2, f"{value.percentage_finished}%")
                i += 1          


            #Budget consommé est entre 101 - 150 %
            sheet4 = workbook.add_worksheet('Budget 101-150%')
            sheet4.write(0,0,'Budget consommée entre 101-150%',titre)
            sheet4.write(2,1,'Nom du projet',entete)
            sheet4.write(2,2,'Budget consommé',entete)
            report_3 = projects.filtered(lambda project: project.percentage_finished >= 101 and project.percentage_finished <= 150 )
            for i,value  in enumerate(report_3) :
                i += 3
                sheet4.write(i, 1, value.name)
                sheet4.write(i, 2, f"{value.percentage_finished}%")
                i += 1   

            #Budget consommé est entre > 150%
            sheet5 = workbook.add_worksheet('Budget >150%')
            sheet5.write(0,0,'Budget consommée supérieur à 150%',titre)
            sheet5.write(2,1,'Nom du projet',entete)
            sheet5.write(2,2,'Budget consommé',entete)
            report_4 = projects.filtered(lambda project: project.percentage_finished >= 150 )
            for i,value  in enumerate(report_4) :
                i += 3
                sheet5.write(i, 1, value.name)
                sheet5.write(i, 2, f"{value.percentage_finished}%")
                i += 1   

            
            






