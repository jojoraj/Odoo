# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    partner_id = fields.Many2one('res.partner')
    location = fields.Char(track_visibility = 'onchange')
    location_dest = fields.Char(track_visibility = 'onchange')
    date_dest = fields.Datetime(track_visibility = 'onchange')
    breakpoint = fields.Char(track_visibility = 'onchange')
    kanban_state = fields.Selection([
        ('done', 'Green'),
        ('blocked', 'Red')], string='Vehicle State',
        copy=False, default='done', track_visibility = 'onchange', required=True)
    is_ambulance = fields.Boolean(compute='compute_is_ambulance')
    driver_ids = fields.Many2one('res.partner',compute='compute_is_ambulance')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(FleetVehicle, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(result['arch'])
        if view_type == 'form':
            context = "{'default_category_id':[%s]}" %(self.env.ref('choldata_fleet.driver_category').id)
            for node in doc.xpath("//field[@name='driver_id']"):
                node.set('context', context)
        result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def write(self, values):
        res = super(FleetVehicle, self).write(values)
        for rec in self:
            if rec.driver_id:
                rec.driver_id.write({
                    'vehicle_id': rec.id,
                    'location': rec.location,
                    'location_dest': rec.location_dest,
                    'date_dest': rec.date_dest,
                    'driver_color': '#000000',
                })
        return res

    @api.model
    def create(self, vals):
        new_id = super(FleetVehicle, self).create(vals)
        if new_id.driver_id:
            new_id.driver_id.write({
                'vehicle_id': new_id.id,
                'location': new_id.location,
                'location_dest': new_id.location_dest,
                'date_dest': new_id.date_dest,
                'driver_color': '#000000',
            })
        return new_id

    @api.depends('tag_ids')
    def compute_is_ambulance(self):
        for rec in self:
            rec.is_ambulance = False
            rec.driver_ids = False
            tag = self.env.ref('choldata_fleet.amb_vehicle_tag')
            if tag.id in rec.tag_ids.ids:
                rec.is_ambulance = True
                rec.driver_ids = self.env['res.partner'].search([('vehicle_id','=',False),('category_id', 'in', [self.env.ref('choldata_fleet.driver_category').id])])

    @api.onchange('tag_ids')
    def set_driver_domain(self):
        tag = self.env.ref('choldata_fleet.amb_vehicle_tag')
        if self.tag_ids and tag.id in self.tag_ids.ids:
            return {'domain': {'driver_id': [('id', '=', self.driver_ids.ids)]}}