from odoo import fields, models, api, exceptions


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'


    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """ Main public API to add followers to a record set. Its main purpose is
        to perform access rights checks before calling ``_message_subscribe``. """
        if not self or (not partner_ids and not channel_ids):
            return True

        partner_ids = partner_ids or []
        channel_ids = channel_ids or []
        adding_current = set(partner_ids) == set([self.env.user.partner_id.id])
        customer_ids = [] if adding_current else None

        if not channel_ids and partner_ids and adding_current:
            try:
                self.check_access_rights('read')
                self.check_access_rule('read')
            except exceptions.AccessError:
                return False
        else:
            self.check_access_rights('read')
            self.check_access_rule('read')

        # filter inactive
        if partner_ids and not adding_current:
            partner_ids = self.env['res.partner'].sudo().search([('id', 'in', partner_ids), ('active', '=', True)]).ids

        return self._message_subscribe(partner_ids, channel_ids, subtype_ids, customer_ids=customer_ids)
