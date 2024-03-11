# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree

class OperationTransfert(models.Model):
    _inherit = 'operation.transfert'

    vehicle_id = fields.Many2one('fleet.vehicle')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(OperationTransfert, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(result['arch'])
        if view_type == 'form':
            domain = "[('tag_ids', 'in', [%s])]" % (self.env.ref('choldata_fleet.amb_vehicle_tag').id)
            for node in doc.xpath("//field[@name='vehicle_id']"):
                node.set('domain', domain)
        result['arch'] = etree.tostring(doc)
        return result