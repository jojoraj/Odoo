from odoo import api, fields, models


class FleetVehicleFuel(models.Model):
    _name = 'fleet.vehicle.fuel'
    _description = 'Fuel log for a vehicle'
    _order = 'date desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    date = fields.Datetime(default=fields.Datetime.now())
    date_search = fields.Date(compute='_compute_date', store=True)
    driver_id = fields.Many2one('res.partner', 'Driver', invisible=True, tracking=True,
                                help='Driver address of the vehicle',
                                copy=False)
    address = fields.Text('Localisation')
    volume = fields.Float(string='Volume (L)')
    odometer = fields.Float(string='Odomètre (Km)',
                            help='Odometer measure of the vehicle at the moment of this log')
    address = fields.Text(string='Adresse')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Véhicule')

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            rec.date_search = rec.date.date()

    @api.depends('vehicle_id', 'date')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name
