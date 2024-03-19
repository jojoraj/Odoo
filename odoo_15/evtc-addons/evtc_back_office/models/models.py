from lxml import etree
from odoo import SUPERUSER_ID, api, models


class EvtcCrmSecurity(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
            remove button create in model crm.lead will current user
            has not admin access or user_root access.
            give access for those users who have group security_crm_groups
        """
        res = super(EvtcCrmSecurity, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type != 'search' and self.env.uid != SUPERUSER_ID:
            has_crm_group = self.env.user.has_group('evtc_back_office.security_crm_groups')
            has_root_groups = self.env.user.has_group('base.user_root')
            has_admin_groups = self.env.user.has_group('base.user_admin')
            if not has_admin_groups or not has_root_groups or not has_crm_group:
                root = etree.fromstring(res['arch'])
                root.set('create', 'false')
                res['arch'] = etree.tostring(root)
        return res
