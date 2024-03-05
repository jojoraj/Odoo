from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    member_ids = fields.Many2many('res.users', 'team_user_rel', 'sale_team_id', 'user_id', string="Member channel")
