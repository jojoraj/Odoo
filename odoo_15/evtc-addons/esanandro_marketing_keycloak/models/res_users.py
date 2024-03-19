import random
import string

from odoo import _, api, models


class EsanKeycloak(models.Model):
    _inherit = 'res.users'

    @api.model
    def ext_partner_json_dump(self, data=None, size=False):
        data = data if data else []
        if size:
            users = self.env['res.users'].search([], limit=size).filtered(lambda user: not user.has_group('base.group_user') and user.login_date)
        else:
            users = self.env['res.users'].search([]).filtered(lambda user: not user.has_group('base.group_user') and user.login_date)
        for rec in users:
            login = rec.login.replace(' ', '')[1:]
            if list(filter(lambda user: user['username'] == login, data)):
                continue
            firstname, lastname = '', ''
            name = rec.name.strip()
            if ' ' in name:
                users_name = name.split(' ')
                firstname += users_name[-1]
                lastname += ' '.join(users_name[:len(users_name) - 2])
            else:
                lastname += rec.name

            if lastname and not firstname:
                firstname = lastname
                lastname = ''

            values = {
                "username": login,
                "lastName": lastname,
                "firstName": firstname,
                "email": rec.partner_id.email if rec.partner_id else '',
                "attributes": {
                    "country_code": rec.country_id.code,
                    "street": rec.partner_id.street
                },
                "credentials": [
                    {
                        "type": "password",
                        "value": self.generate_random_password(),
                        "temporary": True
                    }
                ],
                "enabled": True
            }
            data.append(values)
        return data

    def generate_random_password(self):
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
        random.shuffle(characters)
        password = []
        for _i in range(9):
            password.append(random.choice(characters))
        random.shuffle(password)
        return "".join(password)

    @api.model
    def send_marketing_sms(self, users):
        for user in users:
            attributes = user.get("attributes", False)
            credentials = user.get('credentials')[0]
            if attributes and attributes.get('country_code', '') == 'MG':
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
                message = _(f"Bonjour , Suite à une mise à jour du système, "
                            f"merci de vous reconnecter avec le même identifiant et le mdp : {credentials['value']}")
                values = {
                    'name': message,
                    'partner_id': partner_id,
                    'mobile': user['username'],
                    'state': 'sending',
                    'gateway_id': gateway_id,
                }
                sms_id = sms_queue.create(values)
                sms_id.action_send()
                return sms_id.id
            else:
                template = self.env.ref('esanandro_marketing_keycloak.email_marketing_esanandro')
                try:
                    template.write({
                        'email_to': user.get('email')
                    })
                    template.with_context(
                        lastname=user.get('lastName', ''),
                        temporary_password=credentials.get('value', '')
                    ).send_mail(2, force_send=True, raise_exception=True)
                except Exception as e:
                    return e
                return True
