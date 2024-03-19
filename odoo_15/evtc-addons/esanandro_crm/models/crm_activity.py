# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models, modules

_logger = logging.getLogger(__name__)
LEAD = 'crm.lead'
FIELDS_COUNT = 'pick_up_datetime'


class WebsiteFields(models.Model):
    _inherit = 'crm.lead'

    by_website = fields.Boolean(default=False)


class CrmActivities(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    @api.model
    def systray_get_activities(self):
        """ will be appeared in activity menu.
            Making activity always visible with number of today opportunity on label. If there is no opportunity,
            activity menu not visible for lead.
        """
        activities = super(CrmActivities, self).systray_get_activities()
        label = _('Opportunitée depuis le site web')
        lead = self.env[LEAD]
        domain = [('stage_id', '=', 1), ('by_website', '=', True)]
        datatime_now = fields.Datetime.today(self)
        datetime_now_begin = datatime_now.replace(hour=0, minute=0, second=0)
        datetime_now_end = datatime_now.replace(hour=23, minute=59, second=59)
        superiority = [(FIELDS_COUNT, '>=', datetime_now_end)]
        inferiority = [(FIELDS_COUNT, '<=', datetime_now_begin)]
        td_count = lead.search_count(
            domain + [(FIELDS_COUNT, '>=', datetime_now_begin)] + [(FIELDS_COUNT, '<=', datetime_now_end)])
        ord_count = lead.search_count(domain + inferiority)
        pl_count = lead.search_count(domain + superiority)
        activities.append({
            'type': 'activity',
            'name': label,
            'model': 'crm.record.lead',
            'icon': modules.module.get_module_icon(lead._original_module),
            'total_count': td_count + ord_count + pl_count,
            'today_count': td_count,
            'overdue_count': ord_count,
            'planned_count': pl_count,
        })
        return activities

    def get_domain(self, filter_tmp=''):
        domain = [['stage_id', '=', 1], ['by_website', '=', True]]
        datatime_now = fields.Datetime.today(self)
        datetime_now_begin = datatime_now.replace(hour=0, minute=0, second=0)
        datetime_now_end = datatime_now.replace(hour=23, minute=59, second=59)
        superiority = [FIELDS_COUNT, '>=', datetime_now_end]
        inferiority = [FIELDS_COUNT, '<=', datetime_now_begin]
        if filter_tmp == 'today':
            domain += [[FIELDS_COUNT, '<=', datetime_now_end]] + [[FIELDS_COUNT, '>=', datetime_now_begin]]
        elif filter_tmp == 'overdue':
            domain += [inferiority]
        elif filter_tmp != 'my':
            domain += [superiority]
        return [domain]
