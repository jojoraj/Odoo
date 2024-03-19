import logging
import threading
import time

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def default_get(self, fields_list):
        res = super(ResUsers, self).default_get(fields_list)
        if 'groups_id' in res:
            res['groups_id'].append(self.env.ref('fleet_security.administrator_cost').id)
        return res

    @api.model
    def run_administrator_cost(self):
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('fleet_security.administrator_cost'):
                continue
            user.write({'groups_id': [(4, self.env.ref('fleet_security.administrator_cost').id)]})
        _logger.info('end thread: update res.user groups')

    @api.model
    def _add_user_to_group(self):
        t = threading.Thread(target=self.run_administrator_cost())
        t.daemon = True
        t.start_time = time.time()
        _logger.info('start thread: update res.user groups')
        t.start()
