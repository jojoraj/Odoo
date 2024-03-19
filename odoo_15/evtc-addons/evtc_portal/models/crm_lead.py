from odoo import _, fields, models

class MailContent(models.Model):
    _inherit = 'crm.lead'

    partner_notice = fields.Selection([
        ('0', _('')),
        ('1', _('Pas du tout satisfait')),
        ('2', _('Pas satisfait ')),
        ('3', _('Moyen')),
        ('4', _('Satisfait')),
        ('5', _('Tout à fait satisfait')),
    ], default='0')
    
    real_duration = fields.Float('Real duration',compute="_compute_real_duration")

    def _compute_real_duration(self):
        for rec in self:
            if rec.order_ids:
                rec.real_duration = sum(rec.order_ids.mapped('real_duration'))
            else:
                rec.real_duration = rec.duration

