from odoo import fields, models


class ChangeDriver(models.Model):
    _name = 'change.driver'

    name = fields.Char(required=True)
    # default_hour = fields.Float(string='Default hour')
    hours_ids = fields.One2many('change.driver.hours', 'change_driver_id', string='Hour of change of driver')


class ChangeDriverHours(models.Model):
    _name = 'change.driver.hours'

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    hour = fields.Float(string='Changeover time ', required=True)

    change_driver_id = fields.Many2one('change.driver', string='Driver change program')
