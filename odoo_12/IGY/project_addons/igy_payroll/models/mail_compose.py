# -*- coding: utf-8 -*-
from odoo import models,fields,api,_

class MailComposeInherit(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.multi
    def action_send_mail(self,context=None):
        context = context or {}
        if context.get('igy_payroll_id') :
            igy_payroll_id = context.get('igy_payroll_id')
            igy_payroll = self.env['igy.payroll'].search([('id','=',igy_payroll_id)],limit=1)
            if igy_payroll :
                igy_payroll.write({
                    'status':'envoye'
                })
        self.send_mail()
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}
