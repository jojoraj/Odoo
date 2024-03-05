from odoo import api, fields, models


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    send_to_employees = fields.Boolean(string="Envoyer aux employees", default=False)

    @api.onchange('send_to_employees')
    def change_send_to_employees(self):
        for rec in self:
            if rec.send_to_employees:
                user_ids = self.env['hr.employee'].sudo().search([]).mapped('user_id')
                partner_ids = user_ids.mapped('partner_id').filtered(lambda partner: partner.email)
                rec.partner_ids = partner_ids
            else:
                rec.partner_ids = False
