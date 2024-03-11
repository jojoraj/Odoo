# -*- coding: utf-8 -*-

from odoo import models, api, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    fleet_count = fields.Integer(compute="_compute_count_fleet", string='Ambulance')
    location = fields.Char()
    location_dest = fields.Char()
    date_dest = fields.Datetime()
    vehicle_id = fields.Many2one('fleet.vehicle')
    driver_color = fields.Char()


    def _compute_count_fleet(self):
        Fleet = self.env['fleet.vehicle']
        for rec in self:
            rec.fleet_count = Fleet.search_count([('partner_id', '=', rec.id)])

    @api.multi
    def return_fleet_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', xml_id)
            res.update(
                context=dict(self.env.context, default_partner_id=self.id, default_tag_ids=[self.env.ref('choldata_fleet.amb_vehicle_tag').id],group_by=False),
                domain=[('partner_id', '=', self.id),('tag_ids', 'in', [self.env.ref('choldata_fleet.amb_vehicle_tag').id])]
            )
            return res
        return False