from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


def striphtml(data):
    p = re.compile(r'<.*?>')
    return re.sub(p,'', data)


class FAQ(models.Model):
    _name = 'faq.simple'
    _inherit = ['mail.thread']
    _description = 'faq'
    _order = 'sequence'

    active = fields.Boolean(default=True)
    question = fields.Char(string="Question", required=True)
    response = fields.Html(string="Response", default="")
    response2 = fields.Html(string="Response", compute="_compute_response", store=True)
    sequence = fields.Integer(string="Sequence", default=lambda self: self.get_default_sequence())
    model_id = fields.Many2one('faq.models', string="Modèle")

    @api.multi
    @api.depends('question')
    def name_get(self):
        result = []
        for line in self:
            if len(line.question) > 30:
                result.append((line.id, line.question[:30] + " ..."))
            else:
                result.append((line.id, line.question))
        return result

    @api.model
    @api.depends('response')
    def _compute_response(self):
        for rec in self:
            rec.response2 = striphtml(rec.response)

    def get_default_sequence(self):
        next_sequence = 1
        last_sequence = self.search([
            ('sequence', '!=', False)
        ], limit=1, order='sequence desc')
        if last_sequence:
            next_sequence = last_sequence.sequence + 1
        return next_sequence

    @api.constrains('sequence')
    def check_unique_sequence(self):
        for rec in self:
            if rec.sequence:
                existing_sequence = self.search([
                    ('sequence', '=', rec.sequence),
                    ('id', '!=', rec.id)
                ])
                if existing_sequence:
                    # Get the last sequence to indicate user
                    last_sequence = self.search([
                        ('sequence', '!=', False)
                    ], limit=1, order='sequence desc')
                    next_sequence = last_sequence.sequence + 1
                    raise ValidationError(('Cette séquence est déja utilisée, utilisez plutôt la prochaine séquence: %s') % (next_sequence))
