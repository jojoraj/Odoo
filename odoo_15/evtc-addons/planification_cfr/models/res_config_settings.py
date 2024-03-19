from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    average_pickup_duration_driver = fields.Float(string='Average recovery time by the driver',
                                                  config_parameter='cfr.average_pickup_duration_driver')
    additional_trip = fields.Many2one('additional.trip', string='Additional trip outside of gmap',
                                      config_parameter='cfr.additional_trip')
    pickup_airport_time_to_add = fields.Float(string='Time to add for airport runs',
                                              config_parameter='cfr.airport_time_to_add')
    pickup_traffic = fields.Float(string='Traffic time between two trips', config_parameter='cfr.pickup_traffic')
    average_delivery_duration_driver = fields.Float(
        string='Average time for the driver to put the vehicle back on the road',
        config_parameter='cfr.average_delivery_duration_driver')
    delivery_airport_time_to_add = fields.Float(string='Time to add for airport runs',
                                                config_parameter='cfr.delivery_airport_time_to_add')
    delivery_traffic = fields.Float(string='Traffic time between two trips', config_parameter='cfr.delivery_traffic')
    break_duration = fields.Float(config_parameter='cfr.break_duration')
    begin_time_window = fields.Float(string='Start of break window', config_parameter='cfr.begin_time_window')
    end_time_window = fields.Float(string='End of break window', config_parameter='cfr.end_time_window')
    factitious_course = fields.Float(string='Duration of the mock course', config_parameter='cfr.factitious_course')
    soft_start_datetime = fields.Float(string='Beginning of the daytime range',
                                       config_parameter='cfr.soft_start_datetime')
    soft_end_datetime = fields.Float(string='End of the daytime range', config_parameter='cfr.soft_end_datetime')
    base_url_cfr = fields.Char(string='Base url for CFR API', config_parameter='cfr.base_url_cfr', required=True)
    client_id = fields.Char(required=True)
    client_secret = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    base_url_token = fields.Char(required=True)
    date_expiration = fields.Datetime('Token Validity', copy=False, readonly=1)
    cfr_access_token = fields.Char(readonly=1)
    cfr_refresh_token = fields.Char(readonly=1)

    def cfr_generate_token(self):
        self.env['crm.lead'].sudo().generate_token()

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('cfr.client_id', self.client_id)
        self.env['ir.config_parameter'].set_param('cfr.client_secret', self.client_secret)
        self.env['ir.config_parameter'].set_param('cfr.username', self.username)
        self.env['ir.config_parameter'].set_param('cfr.password', self.password)
        self.env['ir.config_parameter'].set_param('cfr.base_url_token', self.base_url_token)
        self.env['ir.config_parameter'].set_param('cfr.cfr_access_token', self.cfr_access_token)
        self.env['ir.config_parameter'].set_param('cfr.cfr_refresh_token', self.cfr_refresh_token)
        self.env['ir.config_parameter'].set_param('cfr.date_expiration', self.date_expiration)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'client_id': params.get_param('cfr.client_id'),
            'client_secret': params.get_param('cfr.client_secret'),
            'username': params.get_param('cfr.username'),
            'password': params.get_param('cfr.password'),
            'base_url_token': params.get_param('cfr.base_url_token'),
            'cfr_access_token': params.get_param('cfr.cfr_access_token'),
            'cfr_refresh_token': params.get_param('cfr.cfr_refresh_token'),
            'date_expiration': params.get_param('cfr.date_expiration'),
        })
        return res
