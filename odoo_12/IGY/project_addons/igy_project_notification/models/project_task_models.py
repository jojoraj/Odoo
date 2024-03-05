# -*- coding: utf-8 -*-

import logging
import werkzeug
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class InheritProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, values):
        for line in self:
            if line.project_id and line.project_id.send_mail_change_stage:
                if 'stage_id' in values:
                    new_stage_res = self.env['project.task.type'].sudo().browse([values.get('stage_id')])
                    email_to = line.project_id.manager_ids.mapped('partner_id.email')
                    #TODO a decommenter si le responsable doit etre informer du changement d'etape du tâche
                    # email_to.append(line.project_id.user_id.partner_id.email)

                    mail_obj = self.env['mail.mail']

                    if self.env.user.partner_id.name and line.name and line.project_id.name and new_stage_res.name and line.stage_id.name and len(
                            email_to) > 0:
                        body_html = """
                        <p>Bonjour, <br>
                        L'employé {0} a passé le ticket <b>{1}</b> du projet <b>{2}</b> de l'étape <b>"{3}"</b> à <b>"{4}".</b> </p> <br>
                        Voir la tâche <a href="{5}">ICI</a>
                        """.format(
                            self.env.user.partner_id.name,
                            line.name,
                            line.project_id.name,
                            line.stage_id.name,
                            new_stage_res.name,
                            self.format_url_to_task(line)
                        )
                        email_to = ",".join(email_to)
                        try:
                            mail = mail_obj.sudo().create({
                                'subject': """Notification de changement d'etape de la tache""",
                                'body_html': body_html,
                                'email_from': self.env.user.company_id.email,
                                'auto_delete': True,
                                'email_to': email_to,
                                'state': 'outgoing',
                                'notif_layout': 'mail.mail_notification_light',
                            })
                            mail.send()
                        except:
                            pass

        return super(InheritProjectTask, self).write(values)

    def format_url_to_task(self, task_id):
        """
            Format url to redirect to project task
        """
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += '/mail/view?model=%s&res_id=%d' % (self._name, task_id.id)

        return url
