# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime, timedelta

import pytz
from odoo import api, fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    datetime_deadline = fields.Datetime('Due Datetime', index=True)

    @api.depends('date_deadline', 'datetime_deadline')
    def _compute_state(self):
        for record in self.filtered(lambda activity: activity.date_deadline):
            tz = record.user_id.sudo().tz
            date_deadline = record.date_deadline
            datetime_deadline = record.datetime_deadline
            if datetime_deadline:
                record.state = self._compute_state_from_date(date_deadline, tz, datetime_deadline)
            else:
                record.state = self._compute_state_from_date(date_deadline, tz)

    @api.model
    def _compute_state_from_date(self, date_deadline, tz=False, datetime_deadline=False):
        if datetime_deadline:
            date_deadline = fields.Datetime.from_string(datetime_deadline)
            if not tz:
                tz = self.env.user.tz or 'UTC'
            datetime_deadline = date_deadline.astimezone(pytz.timezone(tz))
            today_utc = pytz.utc.localize(datetime.utcnow())
            today_tz = today_utc.astimezone(pytz.timezone(tz))
            today = today_tz + timedelta(hours=1)

            if datetime_deadline < today:
                return 'overdue'
            elif today.date() == datetime_deadline.date() and datetime_deadline >= today:
                return 'today'
            else:
                return 'planned'
        else:
            date_deadline = fields.Date.from_string(date_deadline)
            today_default = date.today()
            today = today_default
            if tz:
                today_utc = pytz.utc.localize(datetime.utcnow())
                today_tz = today_utc.astimezone(pytz.timezone(tz))
                today = date(year=today_tz.year, month=today_tz.month, day=today_tz.day)
            diff = (date_deadline - today)
            if diff.days == 0:
                return 'today'
            elif diff.days < 0:
                return 'overdue'
            else:
                return 'planned'

    @api.model
    def get_activity_data(self, res_model, domain):
        activity_domain = [('res_model', '=', res_model)]
        if domain:
            res = self.env[res_model].search(domain)
            activity_domain.append(('res_id', 'in', res.ids))
        # change by Tokill
        grouped_activities = self.env['mail.activity'].read_group(
            activity_domain,
            ['res_id', 'activity_type_id', 'ids:array_agg(id)', 'date_deadline:min(date_deadline)',
             'datetime_deadline:min(datetime_deadline)'],
            ['res_id', 'activity_type_id'],
            lazy=False)
        # filter out unreadable records
        if not domain:
            res_ids = tuple(a['res_id'] for a in grouped_activities)
            res = self.env[res_model].search([('id', 'in', res_ids)])
            grouped_activities = [a for a in grouped_activities if a['res_id'] in res.ids]
        res_id_to_deadline = {}
        activity_data = defaultdict(dict)
        for group in grouped_activities:
            res_id = group['res_id']
            activity_type_id = (group.get('activity_type_id') or (False, False))[0]
            to_comp = (res_id not in res_id_to_deadline or group['date_deadline'] < res_id_to_deadline[res_id])
            res_id_to_deadline[res_id] = group['date_deadline'] if to_comp else res_id_to_deadline[res_id]
            if group['datetime_deadline']:
                state = self._compute_state_from_date(group['date_deadline'], self.user_id.sudo().tz,
                                                      group['datetime_deadline'])
            else:
                state = self._compute_state_from_date(group['date_deadline'], self.user_id.sudo().tz)
            activity_data[res_id][activity_type_id] = {
                'count': group['__count'],
                'ids': group['ids'],
                'state': state,
                'o_closest_deadline': group['datetime_deadline'] if group['datetime_deadline'] else group['date_deadline'],
            }
        activity_type_infos = []
        activity_type_ids = self.env['mail.activity.type'].search(
            ['|', ('res_model', '=', res_model), ('res_model', '=', False)])
        for elem in sorted(activity_type_ids, key=lambda item: item.sequence):
            mail_template_info = []
            for mail_template_id in elem.mail_template_ids:
                mail_template_info.append({"id": mail_template_id.id, "name": mail_template_id.name})
            if elem.id == self.env.ref('mail.mail_activity_data_todo').id:
                activity_type_infos.insert(0, [elem.id, elem.name, mail_template_info])
            else:
                activity_type_infos.append([elem.id, elem.name, mail_template_info])

        return {
            'activity_types': activity_type_infos,
            'activity_res_ids': sorted(res_id_to_deadline, key=lambda item: res_id_to_deadline[item]),
            'grouped_activities': activity_data,
        }
