# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import api, exceptions, fields, models, _

from odoo.tools import pycompat
from odoo.tools.misc import clean_context

_logger = logging.getLogger(__name__)

class MailActivity(models.Model):
    """ An actual activity to perform. Activities are linked to
    documents using res_id and res_model_id fields. Activities have a deadline
    that can be used in kanban view to display a status. Once done activities
    are unlinked and a message is posted. This message has a new activity_type_id
    field that indicates the activity linked to the message. """
    _inherit = 'mail.activity'
    _description = 'Activity'

    @api.multi
    def action_notify(self):
        body_template = self.env.ref('mail.message_activity_assigned')

        for activity in self:
            model_description = self.env['ir.model']._get(activity.res_model).display_name
            body = body_template.render(
                dict(activity=activity, model_description=model_description),
                engine='ir.qweb',
                minimal_qcontext=True
            )

            # #Récuperer les mails des DP des projets correstpoandants
            # mails = []
            # rec_user = self.env.user
            # employees  = rec_user.employee_ids
            # for employee in employees :
            #     projets = employee.project_ids
            #     for projet in projets :
            #         user = projet.user_id
            #         employe = user.employee_ids
            #         for e in employe:
            #             mails.append(e.work_email)

            # #Sending mails     
            # for mail in mails :

            #     email_values = {
            #         'email_to': mail,
            #         'body_html': body,
            #         'subject': ('%s: %s assigned to you') % (activity.res_name, activity.summary or activity.activity_type_id.name)
            #         }

            #     print("""
            #         >>>>>>>>>>>>
            #         >>>>>>>>>>>>
            #         >>>>>>>>>>>>
            #             Test :{}
            #         >>>>>>>>>>> 
            #         >>>>>>>>>>>>
            #         >>>>>>>>>>>>
            #         """.format(mail))

                
            #     #override un email 
            #     template_id = self.env['mail.template'].search([('id','=', 14)], limit=1)
            #     template_id.send_mail(template_id.id, force_send=True, email_values=email_values)

                
            self.env['mail.thread'].message_notify(
                partner_ids=activity.user_id.partner_id.ids,
                body=body,
                subject=_('%s: %s assigned to you') % (activity.res_name, activity.summary or activity.activity_type_id.name),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        record_name=activity.res_name,
                model_description=model_description,
                notif_layout='mail.mail_notification_light'
            )
