# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import _, models,fields
from odoo.addons.vtc_area_destination.models.wait_time import float_time_convert, real_times_abr
import re

logger = logging.getLogger(__name__)


class AutoPlanningWizard(models.Model):
    _inherit = 'sale.order'

    @staticmethod
    def convert_to_datetime_before_write(value) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    
    def get_product_uom_domain(self,uom):
        return [uom.lower(), uom.upper(), uom.capitalize()]

    def get_trip_unit_cost(self):
        orderline_price = self.order_line.filtered(lambda line: line.product_uom.name in self.get_product_uom_domain('km'))
        return orderline_price.price_unit
    
    def _write_real_cost_trip(self, length):
        self.real_cost = self.get_trip_unit_cost() * length
    
    def _compute_realtime(self, time):
        t, m = float_time_convert(time)
        if isinstance(t, str):
            t = int(t)
        if isinstance(m, str):
            m = int(m)
        total = t*60 + m
        area_sudo = self.env['area.time.wait.price'].sudo()
        area = area_sudo.search([
            ('begin_wait_time', '<', total),
            ('end_wait_time', '>=', total),
            ('active', '=', True),
        ])
        price =  area and area.price or 0
        self.real_price_wait_time = price
        showtime = real_times_abr(t, m)
        return showtime

    def convert_sec_to_time_float(self, sec):
        hours = sec // 3600
        minutes = (sec % 3600) / 60
        float_time = hours + (minutes / 60)
        return float_time

    def convert_sec_to_minute(self, seconds):
        return seconds / 60 

    def convert_sec_to_time_str(self, test):
        match = re.search(r'(\d+(\.\d+)?)', test)
        sec = 0
        if match:
            # Extract the matched part (numeric) and convert it to a float
            numeric_part = match.group(1)
            float_value = float(numeric_part)
            sec = float_value
        else:
            sec = 0
        time_delta = datetime.timedelta(seconds=sec)
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_price_wait(self, wait_time):
        # wait time in minute
        if wait_time == 0 : return 0
        price_template = self.env['area.time.wait.price'].search([
            ('begin_wait_time', '<', wait_time),
            ('end_wait_time', '>=', wait_time),
            ('active', '=', True),
        ])
        price =  price_template and price_template.price or 0
        return price



    def set_order_request(self, values=None):
        realcost, realtime = ['real_cost', 'real_time']
        values = values or {}
        collect_errors = {}
        if realtime in values:
            # compute real cost
            real_time_sec = self.convert_sec_to_minute(float(values['real_time']))
            real_price_wait = self.get_price_wait(real_time_sec)
            values['real_price_wait_time'] = real_price_wait
            test = self._compute_realtime(
                values[realtime]
            )
            values[realtime] = self.convert_sec_to_time_str(test)
            self.write({
                'real_price_wait_time': real_price_wait,
                'real_time':self.convert_sec_to_time_str(test)
            })
        for record in self:
            for key in values:
                try:
                    if record._fields[key].type == 'float':
                        if key == 'real_duration':
                            record[key] = self.convert_sec_to_time_float(float(values[key]))
                            continue
                        record[key] = float(values[key])
                    elif record._fields[key].type == 'int':
                        record[key] = int(values[key])
                    elif record._fields[key].type == 'datetime':
                        record[key] = record.convert_to_datetime_before_write(values[key])
                    else:
                        record[key] = values[key]
                except Exception as error:
                    collect_errors[record._fields[key].name] = str(error)
                    logger.warning(str(error))
        return collect_errors


    estimated_duration = fields.Char(string="Estimated duration")
    estimated_distance = fields.Float(string="Estimated distance")
    driver_name = fields.Char(string="Driver name")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def is_product_uom_km(self, _unit):
        return self.product_uom.name in (_unit.lower(), _unit.capitalize(), _unit.upper())

    def template_render_dict(self):
        return dict(
            status=False,
            result= dict(
                quant=0,
                is_km_unit=False,
                priceUnit=0,
                lineNote=str()
            )
        )

    def get_orderline_values(self, role):
        values = self.template_render_dict()
        planning_id = self.env['planning.role'].sudo().browse(int(role))
        if not planning_id and planning_id.vehicle_id and planning_id.vehicle_id.driver_id:
            return values
        for record in self:
            order_id = record.order_id
            if record.is_product_uom_km('km'):
                values['result']['quant'] = order_id.real_distance
                values['result']['is_km_unit'] = True
            else:
                values['result']['quant'] = 1
                values['result']['priceUnit'] = order_id.real_price_wait_time
                values['result']['lineNote'] = _("Time wait: %s ") % order_id.real_time
        if planning_id.vehicle_id.geolocalization_type == 'lmfs':
            values['status'] = True
        return values
