from odoo import api, fields, models, _
import base64
import io
import csv
from odoo.addons.smile_impex.models.import_template import XLSDictReader


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def open_import_employee_wizard(self):
        action = self.env.ref('smile_impex.action_import_hr_employee_view').read()[0]
        action['res_id'] = self.env.ref('igy_import_employee_data.import_hr_employee_template').id
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

    def import_hr_employee(self, **kwargs):
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
                all_reader_rows = []
                for line in self.check_file_type(template):
                    all_reader_rows.append(line)
                total_lines = len(all_reader_rows)


                for row in reader:
                    name = row.get('name')
                    if name:
                        employee_id = self.env['hr.employee'].search([
                            ('name', '=', name)
                        ], limit=1)
                        if employee_id:
                            employee_id.work_email = row.get('work_email')
                            employee_id.payment_type = 'madagascar' if row.get('payment_type') == 'Ingenosya Madagascar' else 'business'
                            employee_id.work_day = row.get('work_day')
                            employee_id.timesheet_cost = row.get('timesheet_cost')
                            employee_id.isi = 'five_percent' if row.get('isi') == '5%' else 'zero_percent'
                            employee_id.computer_freight = row.get('computer_freight')
                            employee_id.advance = row.get('advance')
                            employee_id.other_payment = row.get('other_payment')
                        else:
                            employe_obj = {}
                            employe_obj['name'] = row.get('name')
                            employe_obj['first_name'] = row.get('first_name')
                            employe_obj['work_email'] = row.get('work_email')
                            employe_obj['work_phone'] = row.get('work_phone')
                            employe_obj['payment_type'] = 'madagascar' if row.get('payment_type') == 'Ingenosya Madagascar' else 'business'
                            employe_obj['work_day'] = row.get('work_day')
                            employe_obj['timesheet_cost'] = row.get('timesheet_cost')
                            employe_obj['isi'] = 'five_percent' if row.get('isi') == '5%' else 'zero_percent'
                            employe_obj['computer_freight'] = row.get('computer_freight')
                            employe_obj['advance'] = row.get('advance')
                            employe_obj['other_payment'] = row.get('other_payment')
                            try:
                                self.env['hr.employee'].sudo().create(employe_obj)
                            except Exception as e:
                                logger.error(repr(e))
                                self._cr.rollback()

                    if total_lines != 0:
                        percentage = round((index * 100) / total_lines, -1)
                        logger.info('%s percentage done' % percentage)
                    index += 1

                    self._cr.commit()
                    if index == total_lines:
                        self.env.user.notify_success('Importation terminer avec succes')

            except Exception as e:
                logger.error(repr(e))
                self._cr.rollback()


