import json
import logging
import time

import requests
from odoo import _, api, fields, models

HEADERS = {
    'Content-Type': 'application/json',
}
_logger = logging.getLogger(__name__)


class DatabaseUrls(models.Model):
    _name = 'keycloak.users.urls'

    name = fields.Char(string='Link')
    database_name = fields.Char()
    password = fields.Char(string='Admin Password')


class UserBook(models.Model):
    _name = 'keycloak.users'

    name = fields.Char()
    is_current_db = fields.Boolean(default=True, string='Inclure ce Base')
    urls_ids = fields.Many2many('keycloak.users.urls')
    is_active = fields.Boolean(default=False)
    next_execute = fields.Integer(default=0)
    lists = fields.Text()
    keycloak_id = fields.Many2one('auth.oauth.provider')
    user_expend = fields.Text(default='{}')
    user_unexpend = fields.Text(default='{}')
    current_list = fields.Char(default='{}')
    steps = fields.Integer(default=50)
    size = fields.Integer(string='Nombre Utilisateur')

    @api.model
    def run_marketing(self):
        current = self.env['keycloak.users'].sudo().search([('is_active', '=', True)])
        users = self.env['res.users']
        if len(current) == 1 and current.is_active:
            key = int(current.next_execute)
            data = json.loads(current.lists) if current.lists else dict()
            foreach_data = data.get(key) or data.get(str(key), [])
            lst = json.loads(current.current_list if current.current_list else '{}')
            lst.update({
                str(key): json.dumps(foreach_data)
            })
            for user in foreach_data:
                try:
                    users.send_marketing_sms([user])
                    current.keycloak_id.create_keycloak_user(user)
                    usn = json.loads(current.user_expend if current.user_expend else '{}')
                    usn.update({user.get('username'): user})
                    current.user_expend = json.dumps(usn)
                except ValueError:
                    unsn = json.loads(current.user_unexpend if current.user_unexpend else '{}')
                    unsn.update({user.get('username'): user})
                    current.user_expend = json.dumps(unsn)
                time.sleep(1)
            if key + 1 in list(data) or str(key + 1) in list(data):
                current.next_execute = key + 1
            else:
                if self.name:
                    sms_queue = self.env['sms.queue']
                    partner_id = self.env['res.partner'].browse(1) and 1 or 2
                    gateway = self.env['ir.config_parameter'].sudo().get_param(
                        'bypass_native_sms.orange_gateway_default_id', False)
                    if gateway:
                        gateway_id = gateway.id
                    else:
                        gateway = self.env['sms.gateway'].search([])
                        if gateway:
                            gateway_id = gateway[-1].id
                        else:
                            return _("No sms gateway configure in the system")
                    message = _("tous les utlisateurs à été envoyer sur keycloak Bonne continuation")
                    values = {
                        'name': message,
                        'partner_id': partner_id,
                        'mobile': self.name,
                        'state': 'sending',
                        'gateway_id': gateway_id,
                    }
                    sms_id = sms_queue.create(values)
                    sms_id.action_send()
                current.is_active = False
            message = "L'envoie sms marketing est en cours"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }

    def disptach_user(self, users, step):
        xlen = []
        first = 0
        intervall = step
        for _i in range(0, len(users) // step):
            xlen.append(users[first:intervall])
            intervall += step
            first += step
        values = len(xlen) * step
        xlen.append(users[values:])
        return dict(enumerate(xlen))

    def get_post_json(self, database, password, users):
        return {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute",
                "args": [
                    database,
                    "2",
                    password,
                    "res.users",
                    "ext_partner_json_dump",
                    users
                ]
            }
        }

    def post_json_request(self, url, payload):
        response = requests.request("POST", url, headers=HEADERS, data=json.dumps(payload))
        return json.loads(response.content).get('result')

    def get_urls(self, url):
        url = url if url[-1] == '/' else url + '/'
        return url + 'jsonrpc'

    def keycloak_synchronisation(self):
        users = self.env['res.users']
        all_users = users.ext_partner_json_dump([], self.size if self.size else False) if self.is_current_db else []
        for rec in self.urls_ids:
            if rec.name and rec.database_name and rec.password:
                payload = self.get_post_json(rec.database_name, rec.password, all_users)
                all_users += self.post_json_request(self.get_urls(rec.name), payload)
        dispatched = self.disptach_user(all_users, self.steps)
        for k in self.env['keycloak.users'].sudo().search([('is_active', '=', True)]):
            k.is_active = False
        self.sudo().write({
            'keycloak_id': self._context.get('active_id'),
            'lists': json.dumps(dispatched),
            'is_active': True
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': "L'envoie des utilisateur vers keycloak est en cours",
                'type': 'success',
                'sticky': False,
            }
        }


class Provider(models.Model):
    _inherit = 'auth.oauth.provider'

    def send_user_to_keycloak(self):
        view_id = self.env.ref('esanandro_marketing_keycloak.keycloak_users_view_form').id
        return {
            'name': _('Synchronisation avec Keycloak'),
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': 'keycloak.users',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
