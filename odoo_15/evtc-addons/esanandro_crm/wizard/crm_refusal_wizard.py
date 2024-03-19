from odoo import fields, models


class CrmRefusalWizard(models.TransientModel):
    _name = 'crm.refusal.wizard'
    _description = 'Refusal Pop up'

    refusal_ids = fields.Many2many('crm.refusal', string='Reason for refusal')
    refusal_remark = fields.Text()
    crm_id = fields.Many2one('crm.lead', string='Leads')

    def write_refusal_reason(self):
        crm_lead_id = self.env['crm.lead'].search([('id', '=', self.crm_id.id)])
        stage_id = self.env.ref('esanandro_crm.stage_lead5').id
        crm_lead_id.write({
            'refusal_remark': self.refusal_remark,
            'refusal_ids': [(6, 0, self.refusal_ids.ids)],
            'stage_id': stage_id
        })
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
        return action
