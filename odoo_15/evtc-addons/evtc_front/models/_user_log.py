from datetime import date as Date

from odoo import fields, models


class SessionStore(models.Model):
    _name = 'google.log_session'
    _description = 'log session google map'

    recuperation_with_validation = fields.Integer(string="Recuperation avec Validation", default=0)
    destination_with_validation = fields.Integer(string="Destination avec Validation", default=0)
    recuperation_without_validation = fields.Integer(string="Recuperation sans Validation", default=0)
    destination_without_validation = fields.Integer(string="destination sans Validation", default=0)
    myaccount_without_validation = fields.Integer(string="Mes addresse sans Validation", default=0)
    myaccount_with_validation = fields.Integer(string="Mes addresse avec Validation", default=0)
    partner_id = fields.Many2one('res.partner', string='Utilisateurs')
    record_time = fields.Date(string="Jour")
    record_crm_validation = fields.Integer(string="Crm et addresse valider", default=0)
    details_callback = fields.Float(string="Appel aux services google Place", store=True, default=0)

    def _get_current_time(self):
        return Date.today()

    def _create_record(self, value):
        self.create(value)

    def _update_record_lign(self, work, value):
        work.write(value)

    def _calculated_session_values(self, old_id, record):
        current_data = self.browse(old_id)
        recuperation_with_validation = current_data.recuperation_with_validation + record.get('recuperation_with_validation', 0)
        destination_with_validation = current_data.destination_with_validation + record.get('destination_with_validation', 0)
        recuperation_without_validation = current_data.recuperation_without_validation + record.get('recuperation_without_validation', 0)
        destination_without_validation = current_data.destination_without_validation + record.get('destination_without_validation', 0)
        myaccount_without_validation = current_data.myaccount_without_validation + record.get('myaccount_without_validation', 0)
        myaccount_with_validation = current_data.myaccount_with_validation + record.get('myaccount_with_validation', 0)
        crm_validation = current_data.record_crm_validation + record.get('record_crm_validation', 0)
        record = recuperation_with_validation + destination_with_validation + recuperation_without_validation + destination_without_validation + \
            myaccount_without_validation + myaccount_with_validation
        value = {
            'recuperation_with_validation': recuperation_with_validation,
            'destination_with_validation': destination_with_validation,
            'recuperation_without_validation': recuperation_without_validation,
            'destination_without_validation': destination_without_validation,
            'record_crm_validation': crm_validation,
            'details_callback': record,
            'myaccount_without_validation': myaccount_without_validation,
            'myaccount_with_validation': myaccount_with_validation,
        }
        return value

    def find_current_data(self, partner_id, vals):
        working_lign = self.search([
            ('partner_id', '=', partner_id),
            ('record_time', '=', self._get_current_time())
        ])
        if not working_lign:
            vals.update({
                'record_time': self._get_current_time(),
                'partner_id': partner_id
            })
            self._create_record(vals)
        else:
            related_value = self._calculated_session_values(working_lign.id, vals)
            self._update_record_lign(working_lign , related_value)
