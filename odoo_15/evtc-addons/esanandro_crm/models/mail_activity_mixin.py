# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

import pytz
from odoo import models
from odoo.addons.mail.models.mail_activity_mixin import \
    MailActivityMixin as OriginalMixin

_logger = logging.getLogger(__name__)


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def _search_activity_state(self, operator, value):
        all_states = {'overdue', 'today', 'planned', False}
        if operator == '=':
            search_states = {value}
        elif operator == '!=':
            search_states = all_states - {value}
        elif operator == 'in':
            search_states = set(value)
        elif operator == 'not in':
            search_states = all_states - set(value)

        reverse_search = False
        if False in search_states:
            # If we search "activity_state = False", they might be a lot of records
            # (million for some models), so instead of returning the list of IDs
            # [(id, 'in', ids)] we will reverse the domain and return something like
            # [(id, 'not in', ids)], so the list of ids is as small as possible
            reverse_search = True
            search_states = all_states - search_states

        # Use number in the SQL query for performance purpose
        integer_state_value = {
            'overdue': -1,
            'today': 0,
            'planned': 1,
            False: None,
        }

        search_states_int = {integer_state_value.get(s or False) for s in search_states}

        query = """
              SELECT res_id
                FROM (
                    SELECT res_id,
                           -- Global activity state
                        CASE WHEN datetime_deadline IS NOT NULL AND datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE res_partner.tz < now() AT TIME ZONE res_partner.tz + interval '1 hour' THEN -1
                        WHEN datetime_deadline IS NOT NULL AND datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE res_partner.tz > now() AT TIME ZONE res_partner.tz + interval '1 hour'
                        AND min((datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE res_partner.tz)::date - (now() AT TIME ZONE res_partner.tz)::date) = 0 THEN 0
                        WHEN min((datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE res_partner.tz)::date - (now()AT TIME ZONE res_partner.tz)::date) > 0  THEN 1
         WHEN datetime_deadline IS NULL THEN
                           MIN(
                                -- Compute the state of each individual activities
                                -- -1: overdue
                                --  0: today
                                --  1: planned
                               SIGN(EXTRACT(day from (
                                    mail_activity.date_deadline - DATE_TRUNC('day', %(today_utc)s AT TIME ZONE res_partner.tz)
                               )))
                            )::INT
                        END AS activity_state
                      FROM mail_activity
                 LEFT JOIN res_users
                        ON res_users.id = mail_activity.user_id
                 LEFT JOIN res_partner
                        ON res_partner.id = res_users.partner_id
                     WHERE mail_activity.res_model = %(res_model_table)s
                  GROUP BY res_id, mail_activity.date_deadline, res_partner.tz, mail_activity.datetime_deadline
                ) AS res_record
              WHERE %(search_states_int)s @> ARRAY[activity_state]
            """

        self._cr.execute(
            query,
            {
                'today_utc': pytz.utc.localize(datetime.utcnow()),
                'res_model_table': self._name,
                'search_states_int': list(search_states_int)
            },
        )
        return [('id', 'not in' if reverse_search else 'in', [r[0] for r in self._cr.fetchall()])]

    def _read_progress_bar(self, domain, group_by, progress_bar):
        if self._name == "crm.lead":
            group_by_fname = group_by.partition(':')[0]
            if not (progress_bar['field'] == 'activity_state' and self._fields[group_by_fname].store):
                return super()._read_progress_bar(domain, group_by, progress_bar)

            # optimization for 'activity_state'

            # explicitly check access rights, since we bypass the ORM
            self.check_access_rights('read')
            self._flush_search(domain, fields=[group_by_fname], order='id')
            self.env['mail.activity'].flush(['res_model', 'res_id', 'user_id', 'date_deadline'])

            query = self._where_calc(domain)
            self._apply_ir_rules(query, 'read')
            gb = group_by.partition(':')[0]
            annotated_groupbys = [
                self._read_group_process_groupby(gb, query)
                for gb in [group_by, 'activity_state']
            ]
            groupby_dict = {gb['groupby']: gb for gb in annotated_groupbys}
            for gb in annotated_groupbys:
                if gb['field'] == 'activity_state':
                    gb['qualified_field'] = '"_last_activity_state"."activity_state"'
            groupby_terms, _orderby_terms = self._read_group_prepare('activity_state', [], annotated_groupbys, query)
            select_terms = [
                '%s as "%s"' % (gb['qualified_field'], gb['groupby'])
                for gb in annotated_groupbys
            ]
            from_clause, where_clause, where_params = query.get_sql()
            tz = self._context.get('tz') or self.env.user.tz or 'UTC'
            select_query = """
                SELECT 1 AS id, count(*) AS "__count", {fields}
                FROM {from_clause}
                JOIN (
                    SELECT res_id,
                    CASE
                    WHEN min((datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE res_partner.tz)::date - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date) > 0 THEN 'planned'
                    WHEN ((datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE COALESCE(res_partner.tz, %s)) < ((now() AT TIME ZONE COALESCE(res_partner.tz, %s)) + interval '1 hour')
                    OR (datetime_deadline IS NULL AND min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date) < 0)) THEN 'overdue'
                    WHEN (min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date)) = 0
                    AND (datetime_deadline AT TIME ZONE 'UTC' AT TIME ZONE COALESCE(res_partner.tz, %s))>(now() AT TIME ZONE COALESCE(res_partner.tz, %s) + interval '1 hour') THEN 'today'
                    ELSE null
                    END AS activity_state
                    FROM mail_activity
                    JOIN res_users ON (res_users.id = mail_activity.user_id)
                    JOIN res_partner ON (res_partner.id = res_users.partner_id)
                    WHERE res_model = '{model}'
                    GROUP BY res_id, datetime_deadline, res_partner.tz
                ) AS "_last_activity_state" ON ("{table}".id = "_last_activity_state".res_id)
                WHERE {where_clause}
                GROUP BY {group_by}
            """.format(
                fields=', '.join(select_terms),
                from_clause=from_clause,
                model=self._name,
                table=self._table,
                where_clause=where_clause or '1=1',
                group_by=', '.join(groupby_terms),
            )
            num_from_params = from_clause.count('%s')
            where_params[num_from_params:num_from_params] = [tz] * 7  # timezone after from parameters
            self.env.cr.execute(select_query, where_params)
            fetched_data = self.env.cr.dictfetchall()
            self._read_group_resolve_many2x_fields(fetched_data, annotated_groupbys)
            data = [
                {key: self._read_group_prepare_data(key, val, groupby_dict)
                for key, val in row.items()}
                for row in fetched_data
            ]
            return [
                self._read_group_format_result(vals, annotated_groupbys, [group_by], domain)
                for vals in data
            ]
        else:
            return super()._read_progress_bar(domain, group_by, progress_bar)

OriginalMixin._search_activity_state = MailActivityMixin._search_activity_state
# OriginalMixin._read_progress_bar = MailActivityMixin._read_progress_bar
