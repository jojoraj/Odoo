from odoo import models, api


class TruckFormReport(models.AbstractModel):
    _name = "report.igy_mail_reporting.reporting_cold_cv_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['crm.mail.export'].browse(docids)

        project_won = self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id)])
        len_project_won = len(project_won.mapped(id))

        total_mail_sent_cv = self.env['crm.mail'].search([('mail_type', '=', 'cv')])
        positive_answer = self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id), ('mail_type', '=', 'cv')])
        conversion_rate_cv = (len(positive_answer) * 100) / len(total_mail_sent_cv)

        total_mail_cold = self.env['crm.mail'].search([('mail_type', '=', 'cold')])
        positive_answer = self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id), ('mail_type', '=', 'cold')])
        conversion_rate_cold = (len(positive_answer) * 100) / len(total_mail_cold)

        total_conversion_rate_cv_cold = conversion_rate_cv + conversion_rate_cold

        project_cv_won = self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id), ('mail_type', '=', 'cv')])
        project_cold_won = self.env['crm.mail'].search([('stage_two_id', '=', self.env.ref('igy_custom_crm.bdr_crm_won').id), ('mail_type', '=', 'cold')])
        len_project_cv_won = len(project_cv_won.mapped(id))
        len_project_cold_won = len(project_cold_won.mapped(id))

        negative_answer_cv = self.env['crm.mail'].search([('mail_type', '=', 'cv'), ('stage_id', 'in', [self.env.ref('igy_custom_crm.igy_crm_unqalified').id, self.env.ref('igy_custom_crm.igy_crm_fail').id])])
        negative_answer_cold = self.env['crm.mail'].search([('mail_type', '=', 'cold'), ('stage_id', 'in', [self.env.ref('igy_custom_crm.igy_crm_unqalified').id, self.env.ref('igy_custom_crm.igy_crm_fail').id])])
        len_negative_answer_cv = len(negative_answer_cv.mapped(id))
        len_negative_answer_cold = len(negative_answer_cold.mapped(id))

        total_negative_answer = self.env['crm.mail'].search([('stage_id', 'in', [self.env.ref('igy_custom_crm.igy_crm_unqalified').id, self.env.ref('igy_custom_crm.igy_crm_fail').id])])
        len_total_negative_answer = len(total_negative_answer.mapped(id))

        positive_answer_cv = self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id), ('mail_type', '=', 'cv')])
        positive_answer_cold = self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id), ('mail_type', '=', 'cold')])
        len_positive_answer_cv = len(positive_answer_cv.mapped(id))
        len_positive_answer_cold = len(positive_answer_cold.mapped(id))

        total_positive_answer = self.env['crm.mail'].search([('stage_id', '=', self.env.ref('igy_custom_crm.igy_crm_won').id)])
        len_total_positive_answer = len(total_positive_answer.mapped(id))

        return {
            'doc_ids': docids,
            'doc_model': 'truck.booking',
            'docs': docs,
            'data': data,
            'len_project_won': len_project_won,
            'conversion_rate_cv': conversion_rate_cv,
            'conversion_rate_cold': conversion_rate_cold,
            'total_conversion_rate_cv_cold': total_conversion_rate_cv_cold,
            'len_project_cv_won': len_project_cv_won,
            'len_project_cold_won': len_project_cold_won,
            'len_negative_answer_cv': len_negative_answer_cv,
            'len_negative_answer_cold': len_negative_answer_cold,
            'len_total_negative_answer': len_total_negative_answer,
            'len_positive_answer_cv': len_positive_answer_cv,
            'len_positive_answer_cold': len_positive_answer_cold,
            'len_total_positive_answer': len_total_positive_answer
        }
