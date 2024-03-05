# -*- coding: UTF-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from calendar import monthrange as mr
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
class ProjectReport(models.TransientModel):
    _name = "project.report"
    _order = "sequence"

    date = fields.Date()
    @api.model
    def send_report(self):
        # check if report exists
        template_id = self.env.ref('igy_project_report.mail_template_project')
        if not template_id:
            _logger.critical("No mail template found for project reports")
            return

        today = date.today()
        projects_reports_ids = []

        try:
            res = self.env['project.report'].create({
                'date': today,
            })
            projects_reports_ids.append(res)
        except Exception as e:
            _logger.critical(str(e))
            return

        context = {'projects': projects_reports_ids}

        try:
            print('sending mail')
            template_id.with_context(context).send_mail(projects_reports_ids[0].id,force_send=True)
        except Exception as e:
            _logger.critical(str(e))
        return


