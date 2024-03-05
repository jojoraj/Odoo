from odoo import models
import math



class mailReportXLS(models.AbstractModel):
    _name = 'report.igy_mail_reporting.reporting_cold_cv'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workboo  k, data, lines):

        positive_answer_cold = len((self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold')])).mapped(id))
        positive_answer_cv = len((self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive CV')])).mapped(id))
        format_positive_answer_cold = '{:,}'.format(positive_answer_cold)
        format_positive_answer_cv = '{:,}'.format(positive_answer_cv)

        total_mail_cold = len(self.env['crm.mail'].search([('mail_type', '=', 'cold')]))
        total_positive_answer = positive_answer_cold + positive_answer_cv
        conversion_rate_cold = (positive_answer_cold / total_mail_cold) * 100
        conversion_rate_cold = round(conversion_rate_cold, 2)
        format_total_mail_cold = '{:,}'.format(total_mail_cold)

        total_mail_cv = len(self.env['crm.mail'].search([('mail_type', '=', 'cv')]))
        conversion_rate_cv = (positive_answer_cv / total_mail_cv) * 100
        conversion_rate_cv = round(conversion_rate_cv, 2)
        format_total_mail_cv = '{:,}'.format(total_mail_cv)

        total_conversion_rate_cv_cold = conversion_rate_cv + conversion_rate_cold
        total_conversion_rate_cv_cold = round(total_conversion_rate_cv_cold, 2)

        project_cold_won = len(self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id), ('mail_type', '=', 'cold')]))
        project_cv_won = len(self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id), ('mail_type', '=', 'cv')]))
        format_project_cold_won = '{:,}'.format(project_cold_won)
        format_project_cv_won = '{:,}'.format(project_cv_won)

        project_cold_lost = len(self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_lost').id), ('mail_type', '=', 'cold')]))
        project_cv_lost = len(self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_lost').id), ('mail_type', '=', 'cv')]))
        format_project_cold_lost = '{:,}'.format(project_cold_lost)
        format_project_cv_lost = '{:,}'.format(project_cv_lost)

        total_positive_answer = len(self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id)]))
        format_total_positive_answer = '{:,}'.format(total_positive_answer)

        total_mail_sent = self.env['crm.mail'].search([])
        total_mail_sent = len(total_mail_sent.mapped(id))
        format_total_mail_sent = '{:,}'.format(total_mail_sent)

        total_first_sent = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_first_send').id)])
        positive_answer_cold_1st_sent = (len(total_first_sent) / positive_answer_cold) * 100
        positive_answer_cold_1st_sent = round(positive_answer_cold_1st_sent, 2)

        total_second_send = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_second_send').id)])
        positive_answer_cold_2nd_sent = (len(total_second_send) / positive_answer_cold) * 100
        positive_answer_cold_2nd_sent = round(positive_answer_cold_2nd_sent, 2)

        total_third_send = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_third_send').id)])
        positive_answer_cold_3rd_sent = (len(total_third_send) / positive_answer_cold) * 100
        positive_answer_cold_3rd_sent = round(positive_answer_cold_3rd_sent, 2)

        total_fourth_send = self.env['crm.lead'].search([('tag_ids.name', 'ilike', 'Réponse positive Cold'),
                                                        ('mail_respond', '=', True),
                                                        ('stage_id', '=', self.env.ref('igy_custom_crm.igy_fourth_send').id)])
        positive_answer_cold_4th_sent = (len(total_fourth_send) / positive_answer_cold) * 100
        positive_answer_cold_4th_sent = round(positive_answer_cold_4th_sent, 2)

        self.env.cr.execute("select count(partners) as total from (select count(partner_id) as partners from crm_mail group by partner_id )partners;")
        total_res_partner = self.env.cr.dictfetchone()['total']

        average_mail_sent_partner = total_mail_sent / total_res_partner

        number_after_decimal = average_mail_sent_partner - int(average_mail_sent_partner)

        if number_after_decimal > 0.5:
            average_mail_sent_partner = math.ceil(average_mail_sent_partner)
        else:
            average_mail_sent_partner = math.floor(average_mail_sent_partner)

        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format1.set_border(1)
        format1.set_bg_color('#ffd966')
        format2 = workbook.add_format({'font_size': 14, 'align': 'vcenter'})
        format2.set_border(1)
        format3 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format3.set_border(1)
        format4 = workbook.add_format({'font_size': 14, 'align': 'vcenter'})
        format4.set_font_color('#FF0000')
        format4.set_border(1)
        format5 = workbook.add_format({'font_size': 14, 'align': 'vcenter'})
        format5.set_font_color('#008000')
        format5.set_border(1)

        sheet = workbook.add_worksheet('Mail Reporting')

        col_width_dd = len(list('Mail envoyé par personne en moyenne'))
        col_width_bb = len(list('Réponses positives recues'))

        sheet.set_column('B:B', col_width_bb * 1.307)
        sheet.set_column('C:C', col_width_dd * 1.307)
        sheet.set_column('D:D', col_width_dd * 1.307)
        sheet.set_column('E:E', col_width_dd * 1.307)
        sheet.set_column('F:F', col_width_dd * 1.307)

        sheet.write(1, 1, '', format1)
        sheet.write(1, 2, 'Nombre de réponse positive', format1)
        sheet.write(2, 1, 'Cold', format1)
        sheet.write(3, 1, 'CV', format1)
        sheet.write(1, 3, 'Taux de conversion', format1)
        sheet.write(1, 4, 'Gagnés', format1)
        sheet.write(1, 5, 'Perdus', format1)
        sheet.write(6, 1, 'Etapes envoi Cold', format1)
        sheet.write(7, 1, 'Réponses positive Cold', format1)
        sheet.write(6, 2, '1', format3)
        sheet.write(6, 3, '2', format3)
        sheet.write(6, 4, '3', format3)
        sheet.write(6, 5, '4', format3)
        sheet.write(10, 1, 'Mails total envoyés', format1)
        sheet.write(11, 1, 'Réponses positives recues', format1)
        sheet.write(12, 1, 'Taux de conversion global', format1)
        sheet.write(10, 4, 'Cold envoyés', format1)
        sheet.write(11, 4, 'CV envoyés', format1)
        sheet.write(12, 4, 'Mail envoyé par personne en moyenne', format1)

        sheet.write(2, 2, str(format_positive_answer_cold), format2)
        sheet.write(3, 2, str(format_positive_answer_cv), format2)

        sheet.write(7, 2, str(positive_answer_cold_1st_sent) + " %", format2)
        sheet.write(7, 3, str(positive_answer_cold_2nd_sent) + " %", format2)
        sheet.write(7, 4, str(positive_answer_cold_3rd_sent) + " %", format2)
        sheet.write(7, 5, str(positive_answer_cold_4th_sent) + " %", format2)

        sheet.write(2, 3, str(conversion_rate_cold), format2)
        sheet.write(3, 3, str(conversion_rate_cv), format2)

        sheet.write(2, 4, str(format_project_cold_won), format5)
        sheet.write(3, 4, str(format_project_cv_won), format5)

        sheet.write(2, 5, str(format_project_cold_lost), format4)
        sheet.write(3, 5, str(format_project_cv_lost), format4)

        sheet.write(10, 2, str(format_total_mail_sent), format2)
        sheet.write(11, 2, str(format_total_positive_answer), format2)
        sheet.write(12, 2, str(total_conversion_rate_cv_cold), format2)

        sheet.write(10, 5, str(format_total_mail_cold), format2)
        sheet.write(11, 5, str(format_total_mail_cv), format2)
        sheet.write(12, 5, str(average_mail_sent_partner), format2)

