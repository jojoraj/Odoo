import hashlib
import json

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    tag_vehicle_id = fields.Many2one('fleet.vehicle.tag', compute='_compute_type_vehicle', store=True)
    siid = fields.Char(string='External ID of Middle Office')
    tracking_id_map = fields.Char('Tracking ID')

    @api.model
    def create(self, values):
        values['siid'] = self.generate_siid()
        if values.get('model_category_id', False):
            category_id = self.env['fleet.vehicle.model.category'].browse(values['model_category_id'])
            values['team_id'] = category_id.team_id.id
        lead_id = super(CrmLead, self).create(values)
        if lead_id.stage_id == self.env.ref('crm.stage_lead2'):
            lead_id.vehicle_to_busy(values.get('role_id', lead_id.role_id.id))
        return lead_id

    def write(self, values):
        for rec in self:
            if values.get('stage_id', False) == self.env.ref('esanandro_crm.stage_lead6').id and rec.order_ids:
                rec.order_ids.write({'order_stop_date': fields.datetime.now()})
            if values.get('stage_id', False) == self.env.ref('crm.stage_lead2').id and values.get('role_id', rec.role_id.id):
                role_id = self.env['planning.role'].browse(values.get('role_id', rec.role_id.id))
                self.vehicle_to_busy(role_id)
        return super().write(values)

    @api.model
    def vehicle_to_busy(self, role_id):
        role_id.vehicle_id.write({
            'state_id': self.env.ref('evtc_taxi.busy').id
        })

    @api.depends('role_id')
    def _compute_type_vehicle(self):
        for rec in self:
            if rec.role_id and rec.role_id.vehicle_id.tag_id:
                rec.tag_vehicle_id = rec.role_id.vehicle_id.tag_id.id
            else:
                rec.tag_vehicle_id = False

    @api.model
    def create_crm_lead(self, lead):
        res = super(CrmLead, self).create_crm_lead(lead)
        if isinstance(res, int):
            res = self.env['crm.lead'].browse(res).exists()
        if res.model_category_id.is_taxi:
            res.create_trip_request()
        return res.id

    def create_trip_request(self):
        middle_office_id = self.env['middle.office'].get_default_mo()
        data = json.dumps({
            'clientPhone': self.partner_id.get_formatted_phone(),
            'fromLongitude': float(self.pick_up_long),
            'fromLatitude': float(self.pick_up_lat),
            'fromPlaceName': self.pick_up_zone,
            'toLongitude': float(self.dest_long),
            'toLatitude': float(self.dest_lat),
            'toPlaceName': self.destination_zone,
            'estimatedLength': self.estimated_kilometers,
            'estimatedPrice': self.estimated_price,
            'dateCreated': self.create_date.isoformat(),
            'siid': self.siid
        })
        self.partner_id.mo_add_client()
        return middle_office_id.create_trip_request(data)

    def generate_siid(self):
        return hashlib.sha256(f'{fields.datetime.now()}-{self.id}'.encode('utf-8')).hexdigest()

    def prepare_dashboard_values(self):
        result = super().prepare_dashboard_values()
        result['is_taxi'] = self.model_category_id.is_taxi if self.model_category_id else False
        return result

    def process_order(self, quantity):
        self = self.with_user(SUPERUSER_ID)
        order_ids = self.order_ids.filtered(lambda order: order.state == 'draft')
        total_order = []
        for order in order_ids:
            order_lines = order.order_line.filtered(lambda l: l.product_uom.name in ['km', 'Km', 'KM'])
            for line in order_lines:
                line.product_uom_qty = quantity
                line.qty_delivered = quantity
                line.qty_invoiced = quantity
            total_order.append(order.amount_total)
        total = sum(total_order)
        if not total:
            raise ValidationError(_('No Order found for this payment'))
        self.write({'stage_id': self.env.ref('esanandro_crm.stage_lead6').id})
        return total

    def confirm_order(self):
        self = self.with_user(SUPERUSER_ID)
        order_ids = self.order_ids.filtered(lambda order: order.state == 'draft')
        for order in order_ids:
            order.action_confirm()
        self.stage_id = self.env.ref('crm.stage_lead4').id

    @api.model
    def get_crm_stage(self):
        return {
            'new_request': self.env.ref('crm.stage_lead1'),
            'trip_confirmed': self.env.ref('crm.stage_lead2'),
            'driver_coming': self.env.ref('evtc_taxi.stage_pick_up_client'),
            'in_progress': self.env.ref('crm.stage_lead3'),
            'compta': self.env.ref('crm.stage_lead4'),
            'terminated': self.env.ref('esanandro_crm.stage_lead6'),
            'refused': self.env.ref('esanandro_crm.stage_lead5'),
        }

    @api.model
    def progress_values(self, crm_lead_id):
        lead_id = self.browse(int(crm_lead_id)).exists()
        if lead_id:
            return lead_id.prepare_progress_values()
        return False

    def prepare_progress_values(self):
        values = {'map_url': self.get_tracking_url()}
        crm_stage = self.get_crm_stage()
        progressions = [('50', '0', '0'), ('100', '50', '0'), ('100', '100', '50'), ('100', '100', '100')]
        stages = {
            crm_stage['new_request']: (_('Request being validated'), 1, 'step-one', progressions[0]),
            crm_stage['trip_confirmed']: (_('Connection with a driver'), 2, 'step-two', progressions[1]),
            crm_stage['driver_coming']: (_('Your driver is on his way'), 3, 'step-three', progressions[2]),
            crm_stage['in_progress']: (None, 4, 'step-four', progressions[3]),
            crm_stage['compta']: (None, 4, 'step-four', progressions[3]),
            crm_stage['terminated']: (self.stage_id.name, 4, 'step-four', progressions[3]),
            crm_stage['refused']: (_('The race is refused'), 3, 'step-three', progressions[2])
        }
        if self.stage_id in stages:
            state_label, step, class_step, progression = stages[self.stage_id]
            values.update({
                'state_label': state_label,
                'step': step,
                'class_step': class_step,
                'progression': progression
            })
        else:
            values.update({
                'state_label': 'Unknown step',
                'step': 1,
                'class_step': 'step-one',
                'progression': progressions[0]
            })
        return values

    def get_tracking_url(self):
        middle_office_id = self.env['middle.office'].get_default_mo()
        if middle_office_id:
            return f'{middle_office_id.map_url}?tracking_id={self.tracking_id_map}'
        else:
            return '#'
