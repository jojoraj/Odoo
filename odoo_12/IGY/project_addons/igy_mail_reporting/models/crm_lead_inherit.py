from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    mail_respond = fields.Boolean(string="Mail répondu", default="")
    stage_answer_id = fields.Many2one('crm.stage', string="Etape répondu", readonly=False)
    response_date = fields.Date(string="Date de réponse", readonly=False)

    @api.onchange('mail_respond')
    def change_stage_answer_id(self):
        if self.mail_respond:
            self.stage_answer_id = self.stage_id.id

    @api.onchange('mail_respond')
    def change_response_date(self):
        if self.mail_respond:
            self.response_date = fields.date.today()
