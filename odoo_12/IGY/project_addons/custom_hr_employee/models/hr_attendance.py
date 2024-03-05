# -*- coding: utf-8 -*-

from odoo import models,fields,api


class Attendance(models.Model):
    _inherit="hr.attendance"

    has_edit_right = fields.Char(compute="_define_edit_right")
    delay = fields.Char(string="Motif de retard")
    leaving = fields.Char(string="Sortie en avance")

    @api.model
    def _define_edit_right(self):
        if self.env.user.has_group('hr.group_hr_manager') :
            self.has_edit_right = 'True'
        else:
            self.has_edit_right = 'False'
    

                