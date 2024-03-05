from odoo import api, fields, models


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    minimal_cv_tag_value = fields.Char(string="Valeur minimal incremental CV",
                                       config_parameter='igy_custom_crm.minimal_cv_tag_value',
                                       default='9'
                                       )

    interval_day_first_sent = fields.Integer(string="1er envoi > 2ème envoi (Jours)",
                                             config_parameter='mass_mailing.interval_day_first_sent',
                                             default="14")

    interval_day_second_sent = fields.Integer(string="2ème envoi > 3ème envoi (Jours)",
                                            config_parameter='mass_mailing.interval_day_second_sent',
                                            default="14")

    interval_day_third_sent = fields.Integer(string="3ème envoi > 4ème envoi (Jours)",
                                             config_parameter='mass_mailing.interval_day_third_sent',
                                             default="14")
