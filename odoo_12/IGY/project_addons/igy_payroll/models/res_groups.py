
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.constrains('users')
    def _constraint_users_for_payroll_group(self):
        payroll_manager_group = self.env.ref('igy_payroll.igy_payroll_manager')
        if self.id:
            if self.id == payroll_manager_group.id:
                if len(self.users) > 1:
                    raise ValidationError(_('You cannot have more than 1 users in this group'))


class ResUsers(models.Model):
    _inherit = 'res.users'
    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        payroll_manager_group = self.env.ref('igy_payroll.igy_payroll_manager')
        if len(payroll_manager_group.users) > 1:
            raise ValidationError(_('You cannot add new user to this group'))
        return res
