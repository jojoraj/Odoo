from collections import defaultdict
from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import api, exceptions, fields, models, _

from odoo.tools import pycompat
from odoo.tools.misc import clean_context
import logging
_logger = logging.getLogger(__name__)



class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'
    
    _description = 'Customise mail activity'

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        
        """ Schedule an activity on each record of the current record set.
        This method allow to provide as parameter act_type_xmlid. This is an
        xml_id of activity type instead of directly giving an activity_type_id.
        It is useful to avoid having various "env.ref" in the code and allow
        to let the mixin handle access rights.

        :param date_deadline: the day the activity must be scheduled on
        the timezone of the user must be considered to set the correct deadline
        """
        if self.env.context.get('mail_activity_automation_skip'):
            return False
        if not date_deadline:
            date_deadline = fields.Date.context_today(self)
        if isinstance(date_deadline, datetime):
            _logger.warning("Scheduled deadline should be a date (got %s)", date_deadline)
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        else:
            activity_type = self.env['mail.activity.type'].sudo().browse(act_values['activity_type_id'])

        model_id = self.env['ir.model']._get(self._name).id
        activities = self.env['mail.activity']

        hr_leave_model_id = self.env['ir.model'].search([('model', '=', 'hr.leave')]).id
        for record in self: 
            if hr_leave_model_id == model_id :

                date_debut =( record.date_from + timedelta(hours=3)).strftime("%d-%m-%Y (%H:%M)") if record.date_from else None
                date_fin = (record.date_to + timedelta(hours=3)).strftime("%d-%m-%Y (%H:%M)") if record.date_to else None
                employee_name = record.employee_id.name
                employee_project_lists =  " , ".join(record.employee_id.project_ids.mapped('name'))
                description = record.name
                type = record.holiday_status_id.name    
                note = "Nous vous informons que l'employé " + str(employee_name) + " souhaite prendre congé. <br>\
                        Type :  " + str(type) + " <br>\
                        Période : Du " + str(date_debut) + " au " + str(date_fin) + " <br>\
                        Motif : " + str(description)+ " <br> \
                        Projets sur lesquels il est affecté : " + str(employee_project_lists)           
            create_vals = {
                'activity_type_id': activity_type.id,
                'summary': summary or activity_type.summary,
                'automated': True,
                'note': note,
                'date_deadline': date_deadline, 
                'res_model_id': model_id,
                'res_id': record.id,
            }
            create_vals.update(act_values)
            activities |= self.env['mail.activity'].create(create_vals)

        return activities
