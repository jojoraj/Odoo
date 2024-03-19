from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models


class RequestResultList(models.Model):
    _name = 'request.result.list'

    name = fields.Char(compute='_compute_name_to_display')
    date_of_cron = fields.Datetime(readonly=True)
    request_attachment_id = fields.Many2one('ir.attachment', string='Request File')
    data_request = fields.Binary(string='Request File', related='request_attachment_id.datas')
    data_request_name = fields.Char(string='Request File name', related='request_attachment_id.name')
    result_attachment_id = fields.Many2one('ir.attachment', string='Result File')
    data_result = fields.Binary(string='Result File', related='result_attachment_id.datas')
    data_result_name = fields.Char(string='Result File name', related='result_attachment_id.name')
    request_status = fields.Char()

    @api.depends('date_of_cron')
    def _compute_name_to_display(self):
        for cron in self:
            cron.name = _("Planification for %s", cron.date_of_cron.strftime("%Y-%m-%d"))

    @api.model
    def download_last_file(self, period):
        """Get the last file generate from cfr planification"""
        if period:
            time_to_use_midnight_1 = datetime.strptime(period['end_datetime'], '%Y-%m-%d %H:%M:%S') + relativedelta(days=-1, hour=0, minute=0, second=0)
            time_to_use_midnight_2 = datetime.strptime(period['end_datetime'], '%Y-%m-%d %H:%M:%S') + relativedelta(days=-1, hour=23, minute=59, second=59)
        last_file = self.sudo().search([('date_of_cron', '>', time_to_use_midnight_1), ('date_of_cron', '<', time_to_use_midnight_2)], limit=1, order='date_of_cron DESC')

        if len(last_file):
            attachment_id = last_file.result_attachment_id.sudo()
            return attachment_id.id
