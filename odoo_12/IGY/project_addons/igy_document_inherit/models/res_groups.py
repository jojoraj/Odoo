from odoo import api, fields, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def update_user_groups(self):
        """
           This function migrate the user from DP group to Document Manager Group
        """
        dp_group = self.env['res.groups'].search([('name', 'ilike', 'DP')], limit=1)
        document_group_id = self.env.ref('documents.group_documents_manager')
        if dp_group:
            for user in dp_group.users:
                document_group_id.write({
                    'users': [(4, user.id)]
                })
