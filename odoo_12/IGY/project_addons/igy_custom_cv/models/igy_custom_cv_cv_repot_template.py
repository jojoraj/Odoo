from odoo import api, fields, models


class CvReport(models.AbstractModel):
    _name = 'report.igy_custom_cv.cv_repot_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.employee'].browse(docids)
        employee_docs = []
        for employee in docs:
            employee_skill_ids = employee.employee_skill_ids
            tab_skill_ids = self.get_employee_tab_ids(employee_skill_ids)
            employee.tab_skill_ids = tab_skill_ids

            education_ids = employee.education_ids
            tab_education_ids = self.get_employee_tab_ids(education_ids)
            employee.tab_education_ids = tab_education_ids

            employee_docs.append(employee)

        return {
            'docs': employee_docs
        }

    def get_employee_tab_ids(self, employee_skill_ids):
        total_len_skills = int(len(employee_skill_ids) / 3) + 1
        tab_skill_ids = []
        for i in range(0, total_len_skills):
            sub_tab_skills = []
            for j in range(0, 3):
                try:
                    sub_tab_skills.append(employee_skill_ids[(i * 3) + j])
                except:
                    pass
            tab_skill_ids.append(sub_tab_skills)
        return tab_skill_ids
