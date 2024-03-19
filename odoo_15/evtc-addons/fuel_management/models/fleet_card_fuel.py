from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetCardFuel(models.Model):
    _name = 'fleet.card.fuel'
    _description = 'Vehicle card fuel'
    _order = 'date desc'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicule', compute='_compute_vehicle_id', store=True)
    license_plate = fields.Char(string="Plaque d'immatriculation")
    card_number = fields.Char(string="Num carte")
    date_trans = fields.Datetime(string='Date et heure', compute='_compute_date')
    hour_trans = fields.Integer(string='Heure')
    date = fields.Date()
    qty = fields.Float(string='Quantité')
    geotab_qty = fields.Float(string='Quantité Geotab')
    ticket_number = fields.Char(string='Num ticket')
    kilometers = fields.Float(string='Kilometres')
    label = fields.Char(string='Type carburant')
    label_zone = fields.Char(string='LibZone')
    amount = fields.Monetary('Montant')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    station_name = fields.Char(string='Nom station')
    fuel_gap_selection = fields.Selection([('normal', 'Quantité normale'), ('anormal', 'Quantité anormale')],
                                          string='Ecart de quantité', default='normal',
                                          compute='_compute_fuel_gap', store=True)

    @api.depends('license_plate')
    def _compute_vehicle_id(self):
        for rec in self:
            if rec.license_plate:
                vehicle = rec.env['fleet.vehicle'].search(
                    [('license_plate', 'ilike', rec.license_plate)], limit=1)
                if vehicle:
                    rec.vehicle_id = vehicle
                else:
                    raise ValidationError(
                        _(f"There is no vehicle with license plate {rec.license_plate}")
                    )

    @api.depends('qty', 'geotab_qty')
    def _compute_fuel_gap(self):
        for rec in self:
            gap_alert = self.env.user.company_id.gap_alert
            rec.fuel_gap_selection = 'normal' if abs(rec.geotab_qty - rec.qty) <= gap_alert else 'anormal'
            # if rec.qty == 0 or rec.geotab_qty == 0:
            #     rec.fuel_gap_selection = 'anormal'
            # elif rec.qty and rec.geotab_qty:
            #     if rec.geotab_qty > rec.qty:
            #         rec.fuel_gap_selection = 'anormal'
            #     else:
            #         rec.fuel_gap_selection = 'normal' if abs(rec.geotab_qty - rec.qty) <= gap_alert else 'anormal'
            # else:
            #     rec.fuel_gap_selection = 'normal'

    @api.depends('date', 'hour_trans')
    def _compute_date(self):
        for rec in self:
            if rec.date:
                second, minute, hour = 0, 0, 0
                if rec.hour_trans:
                    second = int(str(rec.hour_trans)[-2:]) if str(rec.hour_trans)[-2:] else 0
                    minute = int(str(rec.hour_trans)[-4: -2]) if str(rec.hour_trans)[-4: -2] else 0
                    hour = int(str(rec.hour_trans)[:2]) if (str(rec.hour_trans)[:2] and len(str(rec.hour_trans)) == 6) else (
                        int(str(rec.hour_trans)[:1]) if (str(rec.hour_trans)[:1] and len(str(rec.hour_trans)) == 5) else 0)
                    hour = abs(hour - 3)
                rec.date_trans = fields.Datetime.to_string(
                    datetime.now().replace(year=rec.date.year, month=rec.date.month, day=rec.date.day, hour=hour,
                                           minute=minute, second=second, tzinfo=None))
            else:
                rec.date_trans = False

    def action_generate_geotab_qty(self):
        for rec in self:
            fuel_card_ids = self.env['fleet.card.fuel'].search(
                [('vehicle_id', '=', rec.vehicle_id.id), ('date', '=', rec.date)], order="date asc")
            fuel_ids = self.env['fleet.vehicle.fuel'].search(
                [('vehicle_id', '=', rec.vehicle_id.id), ('date_search', '=', rec.date)], order="date asc")

            peers = zip(fuel_card_ids, fuel_ids)
            for peer in peers:
                # print(peer)
                peer[0].geotab_qty = peer[1].volume

    @api.onchange("date")
    def _onchange_date(self):
        self.action_generate_geotab_qty()

    @api.model
    def create(self, vals):
        res = super(FleetCardFuel, self).create(vals)
        if res:
            partner_id = self.env["res.partner"].search([("name", "=", f"Station {res.station_name or 'Inconnu'}")])
            if not partner_id:
                partner_id = self.env["res.partner"].create({
                    'name': f"Station {res.station_name or 'Inconnu'}",
                    'company_type': 'company',
                })

            self.env["fleet.vehicle.log.services"].create({
                "date": res.date_trans if res.date_trans else datetime.now(),
                "amount": res.amount,
                "vehicle_id": res.vehicle_id.id,
                "odometer": res.kilometers,
                "service_type_id": self.env.ref("fuel_management.service_type_fuel").id,
                "vendor_id": partner_id.id,
                "state": "done",
            })

        return res
