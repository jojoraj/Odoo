from odoo import api, fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def action_close_dialog(self):
        res = super(MailActivity, self).action_close_dialog()
        active_id = self._context.get('default_res_id')
        reflate_activity_type = self.env.ref('igy_custom_crm.activity_reflate')
        if self._context.get('default_res_model') == 'crm.lead' and active_id and self.activity_type_id.id == reflate_activity_type.id:
            crm_lead_id = self.env['crm.lead'].browse(active_id)
            if crm_lead_id:
                crm_lead_id.sudo().write({
                    'week_relaunch_date': self.date_deadline
                })
        return res
