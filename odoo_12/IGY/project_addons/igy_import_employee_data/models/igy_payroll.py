from odoo import api, fields, models, _
import base64
import csv
import io
from odoo.addons.smile_impex.models.import_template import XLSDictReader
from datetime import datetime
import xlrd


class IgyPayroll(models.Model):
    _inherit = 'igy.payroll'

    def open_igy_payroll_wizard(self):
        action = self.env.ref('smile_impex.action_import_hr_employee_view').read()[0]
        action['res_id'] = self.env.ref('igy_import_employee_data.import_igy_invoice_template').id
        action['target'] = 'new'
        return action

    # Import file
    def check_file_type(self, template):
        reader = False
        if template and 'csv' in template.file_name:
            csv_file = base64.decodebytes(template.file).decode('utf-8-sig')
            csv_data = io.StringIO(csv_file)
            reader = csv.DictReader(csv_data, delimiter=';')

        elif template and 'xlsx' in template.file_name:
            excel_file = base64.decodebytes(template.file)
            reader = XLSDictReader(excel_file, 0)
        return reader

    def import_invoice_igy(self, **kwargs):
        logger = self._context['logger']
        model_import_obj = self.env['ir.model.import.template']
        try:
            template = model_import_obj.browse(kwargs.get('template_id'))
            if not template:
                logger.error(_('There is nothing to import.'))
                return
            reader = self.check_file_type(template)
            if not reader:
                logger.error(_('There is nothing to import, Dict errors.'))

            index = 0
            percentage = 0
            all_reader_rows = []
            for line in self.check_file_type(template):
                all_reader_rows.append(line)
            total_lines = len(all_reader_rows)

            for row in reader:
                employee = row.get('employee_id')
                if employee:
                    employee_id = self.env['hr.employee'].search([
                        ('name', '=', employee)
                    ], limit=1)
                    if employee_id:
                        project_id = self.get_projects(row.get('projects'))
                        new_invoice = self.env['igy.payroll'].sudo().create({
                            'employee_id': employee_id.id,
                            'date_payroll': self.get_date(row.get('date_payroll')),
                            'projects': [(6, 0, [project_id])] if project_id else None,
                            'invoice_number': row.get('invoice_number')
                        })
                if not employee:
                    last_invoice = self.env['igy.payroll'].search([], limit=1, order='id desc')
                    project_id = self.get_projects(row.get('projects'))
                    if last_invoice:
                        last_invoice.sudo().write({
                            'projects': [(4, project_id)] if project_id else None
                        })
                if total_lines != 0:
                    percentage = round((index * 100) / total_lines, -1)
                    logger.info('%s percent done' % percentage)
                index += 1
                self._cr.commit()
                if index == total_lines:
                    self.env.user.notify_success('Importation reussi avec succes')

        except Exception as e:
            logger.error(repr(e))
            self._cr.rollback()

    def get_projects(self, project):
        if project:
            project_id = self.env['project.project'].sudo().search([
                ('name', 'ilike', project)
            ], limit=1)
            if project_id:
                return project_id.id
            else:
                return None
        else:
            return None

    def get_date(self, excel_date):
        try:
            python_date = datetime(*xlrd.xldate_as_tuple(excel_date, 0))
        except:
            python_date = None
        return python_date
