from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    score_outside_soft_time_usage = fields.Float(string='score compared to the number of kilometers',
                                                 help='Score that allows to prioritize low mileage cars at night to residual value',
                                                 compute='_compute_score_outside_soft_time_usage')
    score_per_kilometer = fields.Float(string='score versus cost',
                                       help='Allows you to determine a number between 0 and 1 that represents a vehicle\'s usage score per kilometer',
                                       compute='_compute_score_per_kilometer')
    max_kilometer = fields.Float(string='Maximum mileage(km)')
    last_hour_work = fields.Float(string='Last working hour for the day\'s runs', compute="_compute_last_hour_work")
    consumption_hundred = fields.Float(string='consumption per 100 kilometers')
    fuel_id = fields.Many2one('fuel.cost', 'resource/fuel', compute='_compute_fuel', store=True)
    product_price_cost = fields.Float(string='Prix du carburant', compute='_compute_fuel')
    product_id = fields.Many2one('product.product', string='carburant du véhicule')
    change_driver_id = fields.Many2one('change.driver', string='Dummy course schedule')

    @api.depends('odometer')
    def _compute_score_outside_soft_time_usage(self):
        for rec in self:
            if rec.odometer:
                active_vehicle = rec.env['fleet.vehicle'].search([('active', '=', True)])
                max_odometer_km = max(active_vehicle.mapped('odometer'))
                rec.score_outside_soft_time_usage = rec.odometer / max_odometer_km
            else:
                rec.score_outside_soft_time_usage = 0

    @api.depends('consumption_hundred', 'fuel_id')
    def _compute_score_per_kilometer(self):
        for rec in self:
            self_cost = False
            if rec.fuel_type:
                fuel_id = self.env['fuel.cost'].search([('name', '=', rec.fuel_type)])
                if fuel_id:
                    if fuel_id.cost and rec.consumption_hundred:
                        self_cost = fuel_id.cost * rec.consumption_hundred / 100
                    if self_cost:
                        fleet_ids = self.env['fleet.vehicle'].search([('active', '=', True)])
                        cost_list = []
                        for vehicle in fleet_ids:
                            if rec.fuel_type:
                                fuel_id = self.env['fuel.cost'].search([('name', '=', vehicle.fuel_type)])
                                if fuel_id:
                                    if fuel_id.cost and vehicle.consumption_hundred:
                                        cost_per_km = fuel_id.cost * vehicle.consumption_hundred / 100
                                        cost_list.append(cost_per_km)
                        if len(cost_list) > 0:
                            max_cost = max(cost_list)
                            rec.score_per_kilometer = self_cost / max_cost
                        else:
                            rec.score_per_kilometer = 0
                    else:
                        rec.score_per_kilometer = 0
                else:
                    rec.score_per_kilometer = 0
            else:
                rec.score_per_kilometer = 0

    @api.depends('fuel_type')
    def _compute_fuel(self):
        for rec in self:
            if rec.fuel_type:
                fuel_id = self.env['fuel.cost'].search([('name', '=', rec.fuel_type)])
                if fuel_id:
                    rec.product_price_cost = fuel_id.cost
                    rec.fuel_id = fuel_id.id
                else:
                    rec.product_price_cost = 0
            else:
                rec.product_price_cost = 0


class FleetVehicleModelCategory(models.Model):
    _inherit = 'fleet.vehicle.model.category'

    qualification_level = fields.Integer()
