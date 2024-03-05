from odoo import api, fields, models


class HrPayrollReport(models.Model):
    _name = 'report.hr_payroll_igy.igy_report_payslip'

    @api.model
    def _get_report_values(self, docids, data=None):
        rows = []
        col = []
        i = 1
        for doc_id in docids:
            doc = self.env['hr.payslip'].browse(doc_id)
            col.append(doc)
            col.append(doc)
            if len(col) > 1 or i == len(docids):
                rows.append(col)
                col = []
            i += 1
        return {
            'rows': rows
        }
