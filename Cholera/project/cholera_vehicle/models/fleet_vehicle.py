# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    blacklist = fields.Boolean(default=False)
    
    def name_get(self):
        res = []
        for record in self:
            vehicle_tag_names = record.tag_ids.mapped('name')
            if 'véhicule' in vehicle_tag_names and record.blacklist == True:
                res.append((record.id, "%s/%s(Blacklist)" % (record.license_plate,record.model_id.name)))
            else:
                res.append((record.id, "%s/%s" % (record.license_plate,record.model_id.name)))
        return res