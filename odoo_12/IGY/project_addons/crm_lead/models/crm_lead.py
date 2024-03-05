# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions


class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    motivation = fields.Text('Motif')
    date_changed = fields.Boolean('Date changed', default=False)
    
    # event when date action changed
    @api.onchange('next_send_date')
    def _onchange_date_action(self):
        self.date_changed = True
        self.motivation = False

    def write(self, values):
        if values.get('date_changed') and values['date_changed'] == True:
            if values.get('motivation') and values['motivation'] not in ('', False):
                self.env['mail.message'].create({
                    'date': fields.Datetime.now(),
                    'body': '<p>' + values['motivation'] + '</p>',
                    'model': 'crm.lead',
                    'res_id': self.id,
                    'record_name': self.name,
                    'message_type': 'comment',
                    'author_id': self.env.user.partner_id.id
                })
                values['date_changed'] = False
                values['motivation'] = False
            else:
                raise exceptions.Warning('Merci de saisir la motivation de votre modification')
        return super(CrmLead, self).write(values)
