# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class InheritProjectProject(models.Model):
    _inherit = 'project.project'

    manager_ids = fields.Many2many('res.users', 'project_manager_rel', 'project_id', 'user_id',
                                   string=_("Gestionnaires"))
    send_mail_change_stage = fields.Boolean(string=_("Activer envoi mail en cas de changement d'etape de la tache"))