from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_favorites = fields.Boolean(default=False)
    is_historical = fields.Boolean(default=False)
    latitude = fields.Char(string="latitude Adress")
    longitude = fields.Char(string="Longitude Adress")
    origin_partner_id = fields.Many2one('res.partner')
    partner_child_ids = fields.One2many('res.partner', 'origin_partner_id')

    def _add_partner(self, partner_id, values):
        """
            Add new child_ids in partner_id with values
        :param partner_id:
        :param values:
        """
        new_partner_id = self.sudo().create(values)
        partner_id.sudo().child_ids = [(4, new_partner_id.id)]
        return new_partner_id

    def add_new_contact(self, partner_id, values):
        """
            Add new child_ids in partner_id with values and set if it's an historical partner or favorites
        :param partner_id:
        :param values:
        """

        historical_partner_ids = partner_id.child_ids.filtered(
            lambda c: c.is_historical and c.active and c.latitude and c.longitude)
        valid_history = historical_partner_ids.filtered(
            lambda p: p.latitude == values.get('latitude') and p.longitude == values.get('longitude'))

        # remove duplicate history
        if valid_history and 1 < len(valid_history):
            for h in valid_history[:-1]:
                h.sudo().active = False
            valid_history = valid_history[-1]

        if values.get('is_historical'):
            if valid_history:
                valid_history.sudo().write(values)
            else:
                valid_history = self.sudo()._add_partner(partner_id, values)
            return valid_history

        elif values.get('is_favorites'):
            return self._add_partner(partner_id, values)

    @api.model
    def delete_partner_adress(self, adresse):
        if adresse['is_historical']:
            partner = self.sudo().search(
                [('street', '=', adresse['street']), ('is_historical', '=', True),
                 ('type', '=', 'other')])
        else:
            partner = self.sudo().search(
                [('street', '=', adresse['street']), ('is_favorites', '=', True),
                 ('type', '=', 'other')])
        return partner.sudo().unlink()
