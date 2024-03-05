from odoo import api, fields, models


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def update_mass_mailing_no_update(self):
        cron_id = self.env['ir.model.data'].search([
            ('name', '=', 'ir_cron_mass_mailing_queue')
        ], limit=1)
        if cron_id:
            cron_id.noupdate = False if cron_id.noupdate == True else False