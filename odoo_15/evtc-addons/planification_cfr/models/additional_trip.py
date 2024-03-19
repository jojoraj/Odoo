from odoo import api, fields, models


class AdditionalTrip(models.Model):
    _name = 'additional.trip'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True,
                            help="If the active field is set to false, it will allow you to hide the Working Time without removing it.")
    line_ids = fields.One2many(
        'additional.trip.line', 'additional_trip_id', 'Working Time', copy=True)

    @api.model
    def update_additional_time(self, args):
        additional_trip_id = int(self.env['ir.config_parameter'].sudo().get_param('cfr.additional_trip'))
        additional_lines_ids = self.sudo().browse(additional_trip_id).line_ids
        if additional_lines_ids and args:
            date_lines = additional_lines_ids.filtered(lambda d: int(d.dayofweek) == int(args['date']))
            hours = int(args['hours'])
            minutes = int(args['minutes'])
            seconds = ((hours * 60) + minutes) * 60
            hours_float = seconds / (60 * 60)
            for date_line in date_lines:
                if date_line.hour_from <= hours_float < date_line.hour_to:
                    coefficient = date_line.coefficient
                    # coefficient = '{0:02.0f}:{1:02.0f}'.format(*divmod(coefficient * 60, 60))
                    # additional_time = ((int(coefficient.split(':')[0]) * 60) + int(coefficient.split(':')[1])) * 60
                    # return additional_time
                    return coefficient


class AdditionalTripLine(models.Model):
    _name = 'additional.trip.line'

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    additional_trip_id = fields.Many2one('additional.trip', string='Additional trip')
    hour_from = fields.Float(string='Work from', required=True, index=True,
                             help="Start and End time of working.\n"
                                  "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to', required=True)
    coefficient = fields.Float(required=True)

    @api.onchange('hour_from', 'hour_to')
    def _onchange_hours(self):
        # avoid negative or after midnight
        self.hour_from = min(self.hour_from, 23.99)
        self.hour_from = max(self.hour_from, 0.0)
        self.hour_to = min(self.hour_to, 24)
        self.hour_to = max(self.hour_to, 0.0)

        # avoid wrong order
        self.hour_to = max(self.hour_to, self.hour_from)
