from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def write(self, values):
        self.set_global_lead(values)
        res = super(CrmLead, self).write(values)
        return res

    @api.model
    def create(self, vals):
        self.set_global_lead(vals)
        res = super(CrmLead, self).create(vals)
        res.color = 8
        return res

    def set_global_lead(self, values):
        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_qualification_marketting').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_qualification_marketting').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_qualification_marketing').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_first_send').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_first_send').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_first_send').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_second_send').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_second_send').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_second_send').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_third_send').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_third_send').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_third_send').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_fourth_send').id or self \
                ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_fourth_send').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_fourth_send').id

        if values.get('stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_qualif').id or self\
            ._context.get('default_stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_qualif').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_commercial_qualif').id

        if values.get('stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_proposition').id or self\
            ._context.get('default_stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_proposition').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_proposition').id

        if values.get('stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id or self\
            ._context.get('default_stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_offer_sent').id

        if values.get('stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_won').id or self\
            ._context.get('default_stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_won').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_crm_won').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_crm_unqalified').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_crm_unqalified').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_crm_unqalified').id

        if values.get('stage_id') == self.env.ref('igy_custom_crm.igy_crm_fail').id or self\
            ._context.get('default_stage_id') == self.env.ref('igy_custom_crm.igy_crm_fail').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_crm_fail').id
            
       
        if values.get('stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_lost').id or self\
            ._context.get('default_stage_two_id') == self.env.ref('igy_custom_crm.bdr_crm_lost').id:
            values['global_stage_id'] = self.env.ref('igy_custom_crm.global_crm_lost').id



