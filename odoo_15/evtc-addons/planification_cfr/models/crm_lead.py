import base64
import io
import json
import logging
import tempfile
import threading
import time
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import xlsxwriter

_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'

    qualification_level = fields.Integer(compute='_compute_vehicle_level')

    format_vehicule_qualification = fields.Char(string='Vehicle correct format of qualificationType',
                                                compute='_compute_vehicle_level')

    @api.depends('vehicle_note')
    def _compute_vehicle_level(self):
        for rec in self:
            category1_id = self.env['fleet.vehicle.model.category'].search([('qualification_level', '=', 1)], limit=1)
            if rec.vehicle_note:
                vehicle_type = rec.vehicle_note.split('(')[0]
                category_id = self.env['fleet.vehicle.model.category'].search([('name', '=', vehicle_type)])
                if category_id:
                    rec.qualification_level = category_id.qualification_level
                    rec.format_vehicule_qualification = category_id.name
                else:
                    rec.qualification_level = 1
                    rec.format_vehicule_qualification = category1_id.name
            else:
                rec.qualification_level = 1
                rec.format_vehicule_qualification = category1_id.name

    def get_shipment_data(self):
        date_now = datetime.now()
        # date_now = date_now + relativedelta(day=5, month=7, hour=20, minute=0, second=0)
        tomorrow_midnight = date_now + relativedelta(days=+1, hour=23, minute=59, seconds=59)
        midnight = date_now + relativedelta(days=+1, hour=0, minute=0, second=0)
        first_hour_work = midnight + relativedelta(hours=-3)
        last_hour = tomorrow_midnight + relativedelta(hours=-3)
        shipments = []
        new_request = self.env.ref('crm.stage_lead1')
        crm_lead_obj = self.env['crm.lead'].search(
            [('pick_up_datetime', '>=', first_hour_work), ('pick_up_datetime', '<', last_hour),
             ('stage_id', '=', new_request.id), ('is_location', '=', False), ('as_many_course', '=', False),
             ('out_tana', '=', False)])

        shipments = [{
            "reference": "L" + str(order.id),
            "dateTimePickup": (order.pick_up_datetime + relativedelta(hours=+3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "datePickup": (order.pick_up_datetime + relativedelta(hours=+3)).strftime("%Y-%m-%d"),
            "timePickup": (order.pick_up_datetime + relativedelta(hours=+3)).strftime("%H:%M"),
            "adressePickup": order.pick_up_zone,
            "latitudePickup": float(order.pick_up_lat) if order.pick_up_lat else "",
            "longitudePickup": float(order.pick_up_long) if order.pick_up_long else "",
            "adresseDelivery": order.destination_zone,
            "latitudeDelivery": float(order.dest_lat) if order.dest_lat else "",
            "longitudeDelivery": float(order.dest_long) if order.dest_long else "",
            "qualificationType": order.format_vehicule_qualification,
            "qualificationLevel": order.qualification_level,
            "pickupDuration": self.get_pickup_duration(order.pick_up_datetime, order.duration, order.pick_up_zone),
            "deliveryDuration": int(self.get_delivery_duration(order.pick_up_datetime, order.duration,
                                                               order.destination_zone) * 60 * 60),  # to get from conf
            "loadType": "course",
            "loadAmount": "1",
            "mandatory": False,
        } for order in crm_lead_obj]

        return shipments

    def get_vehicle_data(self):
        date_now = datetime.now()
        midnight = date_now + relativedelta(days=+1, hour=0, minute=0, second=0)
        last_hour = date_now + relativedelta(days=+2, hour=2, minute=0, second=0)
        fleet_obj = self.env['fleet.vehicle'].search(
            [('active', '=', True), ('state_id', '!=', self.env.ref('fleet.fleet_vehicle_state_downgraded').id)])
        fleet_obj = fleet_obj.filtered(lambda x: x.max_kilometer != 0.0 and x.score_outside_soft_time_usage != 0.0 and x.score_per_kilometer != 0.0)
        start_datetime_dict = self.get_latest_lead_for_vehicle()
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        break_duration = int(float(config_parameter_obj.get_param('cfr.break_duration')) * 60) * 60
        start_break_earliest = float(config_parameter_obj.get_param('cfr.begin_time_window'))
        start_break_latest = float(config_parameter_obj.get_param('cfr.end_time_window'))
        softStartDateTime = float(config_parameter_obj.get_param('cfr.soft_start_datetime'))
        softEndDateTime = float(config_parameter_obj.get_param('cfr.soft_end_datetime'))
        soft_start_hour = int(softStartDateTime)
        soft_start_minute = int((softStartDateTime - soft_start_hour) * 60)
        soft_end_hour = int(softEndDateTime)
        soft_end_minute = int((softEndDateTime - soft_end_hour) * 60)
        soft_start = date_now + relativedelta(days=+1, hour=soft_start_hour, minute=soft_start_minute, second=0)
        soft_end = date_now + relativedelta(days=+1, hour=soft_end_hour, minute=soft_end_minute, second=0)
        breakEarliestStartTime = date_now + relativedelta(days=+1, hour=int(start_break_earliest), minute=int(
            (start_break_earliest - int(start_break_earliest)) * 60), second=0)
        breakLatestStartTime = date_now + relativedelta(days=+1, hour=int(start_break_latest), minute=int(
            (start_break_latest - int(start_break_latest)) * 60), second=0)

        vehicles = [{
            "reference": vehicle.license_plate,
            "modele": vehicle.model_id.name,
            "qualificationType": vehicle.model_id.category_id.name,
            "qualificationLevel": vehicle.model_id.category_id.qualification_level,  # to define with newrules
            "startDateTime": midnight.strftime("%Y-%m-%dT%H:%M:%SZ") if not start_datetime_dict.get(vehicle.id,
                                                                                                    False) else
            start_datetime_dict[vehicle.id]['delivery_datetime'].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime": last_hour.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "softStartDateTime": soft_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "softEndDateTime": soft_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scoreOutsideSoftTimeUsage": vehicle.score_outside_soft_time_usage,
            "breakEarliestStartTime": breakEarliestStartTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "breakLatestStartTime": breakLatestStartTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "breakDuration": break_duration,
            "loadType": "course",
            "loadAmount": "1",
            "startLocation": True,
            "startLocationLat": -18.8736933 if not start_datetime_dict.get(vehicle.id, False) else
            start_datetime_dict[vehicle.id]['dest_lat'],  # esanandro_lat by default
            "startLocationLong": 47.5191681 if not start_datetime_dict.get(vehicle.id, False) else
            start_datetime_dict[vehicle.id]['dest_long'],  # esanandro_long by default
            "endLocation": False,
            "routeDistanceLimitMeters": vehicle.max_kilometer * 1000,
            "scorePerKilometer": vehicle.score_per_kilometer,
        } for vehicle in fleet_obj]

        return vehicles

    def get_fictitious(self):
        date_now = datetime.now()
        # date_now = date_now + relativedelta(day=5, month=7, hour=20, minute=0, second=0)
        date_tomorrow = date_now + relativedelta(days=+1, hour=0, minute=0, second=0, seconds=0)
        tomorrow_day = date_tomorrow.weekday()
        factitious_course_duration = float(self.env['ir.config_parameter'].sudo().get_param('cfr.factitious_course'))

        hour_change = int(factitious_course_duration)
        minute_change = int((factitious_course_duration - hour_change) * 60)
        duration_pick_del = int((factitious_course_duration / 2) * 60 * 60)

        vehicle_ids = self.env['fleet.vehicle'].search([('active', '=', True),
                                                        ('state_id', '!=', self.env.ref('fleet.fleet_vehicle_state_downgraded').id)])
        vehicle_ids = vehicle_ids.filtered(lambda
                                           x: x.max_kilometer != 0.0 and x.score_outside_soft_time_usage != 0.0 and x.score_per_kilometer != 0.0)
        fictitious_rate = []
        number_of_dummy_race = 0
        for vehicle in vehicle_ids:
            number_of_dummy_race += 1
            change_driver_id = vehicle.change_driver_id
            hour_of_change = 20
            if change_driver_id:
                hour_of_change_id = self.env['change.driver.hours'].search(
                    [('change_driver_id', '=', change_driver_id.id), ('dayofweek', '=', tomorrow_day)])
                if hour_of_change_id:
                    hour_of_change = hour_of_change_id.hour
            hour_pickup = int(hour_of_change)
            minute_pickup = int((hour_pickup - int(hour_pickup)) * 60)
            datetime_pickup = date_tomorrow + relativedelta(hours=-hour_change, hour=hour_pickup,
                                                            minutes=-minute_change, minute=minute_pickup)

            value = {
                "reference": "L" + vehicle.license_plate + "-" + str(number_of_dummy_race).zfill(2),
                "dateTimePickup": datetime_pickup.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "datePickup": datetime_pickup.strftime("%Y-%m-%d"),
                "timePickup": datetime_pickup.strftime("%H:%M"),
                "adressePickup": 'esanandro',
                "latitudePickup": -18.8736933,
                "longitudePickup": 47.5191681,
                "adresseDelivery": 'esanandro',
                "latitudeDelivery": -18.8736933,
                "longitudeDelivery": 47.5191681,
                "pickupDuration": duration_pick_del,  # to get from conf / to add durée de pic
                "deliveryDuration": duration_pick_del,  # to get from conf
                "loadType": "course",
                "loadAmount": "1",
                "mandatory": True,
                "vehicleReference": vehicle.license_plate,
            }
            fictitious_rate.append(value)
        return fictitious_rate

    def send_request_get_result(self):
        date_now = datetime.now()
        date_tomorrow = date_now + relativedelta(days=+1, hour=0, minute=0, second=0, seconds=0)
        shipment_data = self.get_shipment_data()
        fictitious = self.get_fictitious()
        data = {}
        data["dateReference"] = date_tomorrow.strftime("%Y-%m-%d")
        data["qualificationStricte"] = False
        data["shipments"] = shipment_data + fictitious
        data["vehicles"] = self.get_vehicle_data()

        data_json = json.dumps(data, indent=3)
        file_json_name = 'Requête du ' + date_tomorrow.strftime("%Y-%m-%d") + '.json'
        file_excel_name = 'Planification du ' + date_tomorrow.strftime("%Y-%m-%d") + '.xlsx'
        # save the json in file
        attachment_obj = self.env['ir.attachment'].sudo()
        request_result_obj = self.env['request.result.list'].sudo()
        crf_doc_list_id = request_result_obj.create({
            'date_of_cron': date_now,
            # 'date_of_planification': date_tomorrow.date()
        })
        json_utf8 = data_json.encode('utf-8')
        basedata_save = base64.encodebytes(json_utf8)
        request_json = attachment_obj.create({'name': file_json_name,
                                              'datas': basedata_save,
                                              'res_model': 'request.result.list',
                                              'res_id': crf_doc_list_id.id
                                              })
        crf_doc_list_id.write({'request_attachment_id': request_json.id})
        _logger.info("===============THREADING===============")
        t = threading.Thread(daemon=True, target=self.request_cfr(data_json, crf_doc_list_id, file_excel_name, attachment_obj, 1))
        t.start()

    def request_cfr(self, data_json, crf_doc_list_id, file_excel_name, attachment_obj, i):
        while not crf_doc_list_id.result_attachment_id and i <= 5:
            i += 1
            access_token = self.env['ir.config_parameter'].sudo().get_param('cfr.cfr_access_token')
            if access_token:
                headers = {"Authorization": 'Bearer ' + access_token,
                           "Content-Type": "application/json"}
                status_request = ""
                base_url_cfr = self.env['ir.config_parameter'].sudo().get_param('cfr.base_url_cfr')
                requests_url = base_url_cfr + "/modelAndOptimize"
                req = requests.post(url=requests_url, data=data_json, headers=headers)
                req_status_code = req.status_code
                status_request = "<Response [" + str(req_status_code) + "]> "
                if req.content != b'' and req_status_code == 200:
                    _logger.info("===============REQUEST CRF RESPONSE STATUS 200===============")
                    content = req.json()
                    if content:
                        result = content
                        excel_data64 = self.json_to_xlsx(result)
                        fobj = tempfile.NamedTemporaryFile(delete=False)
                        fobj.write(excel_data64)
                        fobj.close()
                        with open(fobj.name, 'rb') as t_file:
                            xlsx_content = t_file.read()
                        result_excel = attachment_obj.create({'name': file_excel_name,
                                                              'datas': base64.encodebytes(xlsx_content),
                                                              'res_model': 'request.result.list',
                                                              'res_id': crf_doc_list_id.id
                                                              })
                        crf_doc_list_id.write({'result_attachment_id': result_excel.id})
                        _logger.info("===============END WITH RESULT CRF===============")
                elif req_status_code == 401:
                    _logger.info("===============REQUEST CRF RESPONSE STATUS 401===============")
                    self.regenerate_token()
                else:
                    _logger.info("===============REQUEST CRF RESPONSE NO CONTENT===============")
                    if req_status_code == 500:
                        _logger.error(req.reason)
                    status_request += "no-content"
            else:
                raise UserError(_("Access token is missed"))

            crf_doc_list_id.write({'request_status': status_request})
            time.sleep(180)
        if i > 5 and not crf_doc_list_id.result_attachment_id:
            self.send_mail_function(crf_doc_list_id)

    def get_pickup_duration(self, date, duration_gmap, pickup_zone):
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        average_pickup_duration_driver = float(config_parameter_obj.get_param('cfr.average_pickup_duration_driver'))
        pickup_airport_time_to_add = float(config_parameter_obj.get_param('cfr.airport_time_to_add'))
        if pickup_zone:
            pickup_zone_lowercase = pickup_zone.lower()
            if not (pickup_zone_lowercase.find('aéroport') >= 0 or pickup_zone_lowercase.find(
                    'seranam-piaramanidina') >= 0):
                pickup_airport_time_to_add = 0.0
        else:
            pickup_airport_time_to_add = 0.0
        pickup_traffic = float(config_parameter_obj.get_param('cfr.pickup_traffic'))
        additional_trip_id = int(config_parameter_obj.get_param('cfr.additional_trip'))

        additional_trip = self.get_additional_trip(date, additional_trip_id, duration_gmap)
        pickup_duration = int((average_pickup_duration_driver + pickup_airport_time_to_add + pickup_traffic + additional_trip) * 60 * 60)
        return pickup_duration

    def get_additional_trip(self, date, additional_trip=False, duration_gmap=False):
        self.env['ir.config_parameter'].sudo()
        if additional_trip:
            add_trip_id = self.env['additional.trip'].browse(additional_trip)
            date = date + relativedelta(hours=+3)
            weekday = date.weekday()
            add_trip_line_ids = add_trip_id.line_ids
            coefficient = 1
            if add_trip_line_ids:
                daily_count = add_trip_line_ids.filtered(lambda d: int(d.dayofweek) == weekday)
                t = date.time()
                seconds = (t.hour * 60 + t.minute) * 60 + t.second
                hours = seconds / (60 * 60)
                for hour_range in daily_count:
                    if hour_range.hour_from < hours < hour_range.hour_to:
                        coefficient = hour_range.coefficient
            return float((duration_gmap * coefficient - duration_gmap) / 2)
        else:
            return 0.0

    def get_delivery_duration(self, date, duration, destination_zone):
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        average_delivery_duration_driver = float(config_parameter_obj.get_param('cfr.average_delivery_duration_driver'))
        delivery_additional_trip = int(config_parameter_obj.get_param('cfr.delivery_additional_trip'))
        delivery_airport_time_to_add = float(config_parameter_obj.get_param('cfr.delivery_airport_time_to_add'))
        if destination_zone:
            destination_zone_lowercase = destination_zone.lower()
            if not (destination_zone_lowercase.find('aéroport') >= 0 or destination_zone_lowercase.find(
                    'seranam-piaramanidina') >= 0):
                delivery_airport_time_to_add = 0.0
        else:
            delivery_airport_time_to_add = 0.0
        delivery_traffic = float(config_parameter_obj.get_param('cfr.delivery_traffic'))

        hour_duration = int(duration)
        minute_duration = int((duration - hour_duration) * 60)
        delivery_date = date + relativedelta(hours=+hour_duration, minutes=+minute_duration)
        additional_trip = self.get_additional_trip(delivery_date, delivery_additional_trip, duration)
        delivery_duration = average_delivery_duration_driver + delivery_airport_time_to_add + delivery_traffic + additional_trip
        return delivery_duration

    def json_to_xlsx(self, json_datas):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Planning CFR')
        worksheet2 = workbook.add_worksheet('Google/maps/dir')
        headers = [
            "Référence de la course",
            "Statut",
            "modèle de véhicule demandé",
            "Véhicule proposé",
            "Référence du véhicule proposé",
            "Adresse  de récupération",
            "Adresse de remisage",
            "date et heure de récupération prévu",
            "Startdate Planifier",
            "Enddate Palnifier",
        ]
        col = 0
        tasks = json_datas['outputTasks']
        vehicles = json_datas['outputVehicles']
        for h in headers:
            worksheet.write(0, col, h)
            col += 1
        row = 1
        lead_obj = self.env['crm.lead']
        duration_to_remove = self.get_pickup_delivery_duration()
        hour_duration = int(duration_to_remove)
        min_duration = int((duration_to_remove - int(duration_to_remove)) * 60)
        for task in tasks:
            id_after_L = task['reference'].split('L')[1]
            displayed_end_datetime = task['endDate']
            if id_after_L.isnumeric():
                vehicle_note = lead_obj.search([('id', '=', id_after_L)]).vehicle_note
                if vehicle_note:
                    vehicle_note.split('(')[0]
                #     change value endDate from CFR
                if task.get('endDate', False):
                    end_datetime = datetime.strptime(task['endDate'], "%Y-%m-%dT%H:%M:%SZ")
                    end_datetime_change = end_datetime + relativedelta(hours=-hour_duration, minutes=-min_duration)
                    displayed_end_datetime = end_datetime_change.strftime("%Y-%m-%dT%H:%M:%SZ")
            state = task['status']
            if state == "PLANNED":
                status = _('PLANNED')
            if state == "SKIPPED":
                status = _('SKIPPED')
            if state == "INVALID_DATA":
                status = _('INVALID_DATA')

            rows = [
                task['reference'],
                status,
                task['qualificationType'],
                task['vehicleType'],
                task['vehicleRef'],
                task['adressePickup'],
                task['adresseDelivery'],
                task['datePrevu'],
                task['startDate'],
                displayed_end_datetime
            ]
            col = 0
            for r in rows:
                worksheet.write(row, col, r)
                col += 1
            row += 1

        headers_2 = [
            "Référence véhicule",
            "Modèle",
            "Catégorie",
            "Polyligne d'itinéraire",
        ]
        col = 0
        for h in headers_2:
            worksheet2.write(0, col, h)
            col += 1
        row = 1
        for vehicle in vehicles:
            rows = [
                vehicle['reference'],
                vehicle['modele'],
                vehicle['categorie'],
                vehicle['routePolyline'],
            ]
            col = 0
            for r in rows:
                worksheet2.write(row, col, r)
                col += 1
            row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def get_latest_lead_for_vehicle(self):
        date_now = datetime.now()
        crm_midnight = date_now + relativedelta(hour=21, minute=0, second=0)
        vehicle_ids = self.env['fleet.vehicle'].search([('active', '=', True)])
        vehicle_start_datetime = {}

        for vehicle in vehicle_ids:
            role_id = self.env['planning.role'].search([('vehicle_id', '=', vehicle.id)])
            if role_id:
                last_lead = self.env['crm.lead'].search(
                    [('pick_up_datetime', '<', crm_midnight), ('role_id', '=', role_id.id)],
                    order='pick_up_datetime desc', limit=1)
                if last_lead:
                    duration = last_lead.duration
                    delivery_duration = self.get_delivery_duration(last_lead.pick_up_datetime, last_lead.duration,
                                                                   last_lead.destination_zone)
                    total_duration = duration + delivery_duration
                    minute_duration = (total_duration - int(total_duration)) * 60
                    delivery_datetime = last_lead.pick_up_datetime + relativedelta(hours=+int(total_duration),
                                                                                   minutes=+minute_duration)

                    (delivery_duration - int(delivery_duration)) * 60
                    if delivery_datetime > crm_midnight:
                        vehicle_start_datetime[vehicle.id] = {
                            'delivery_datetime': delivery_datetime + relativedelta(hours=+3),
                            'dest_lat': last_lead.dest_lat if last_lead.dest_lat else -18.8736933,
                            'dest_long': last_lead.dest_long if last_lead.dest_long else 47.5191681}
        return vehicle_start_datetime

    def get_pickup_delivery_duration(self):
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        delivery_traffic = float(config_parameter_obj.get_param('cfr.delivery_traffic'))
        pickup_traffic = float(config_parameter_obj.get_param('cfr.pickup_traffic'))
        sum_duration = delivery_traffic + pickup_traffic
        return sum_duration

    def generate_token(self):
        _logger.info("===============START GENERATE TOKEN===============")
        client_id = self.env['ir.config_parameter'].sudo().get_param('cfr.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('cfr.client_secret')
        username = self.env['ir.config_parameter'].sudo().get_param('cfr.username')
        password = self.env['ir.config_parameter'].sudo().get_param('cfr.password')
        requests_url = self.env['ir.config_parameter'].sudo().get_param('cfr.base_url_token')

        if not client_id or not client_secret or not username or not password or not requests_url:
            raise UserError(_("The token Generate service is not configured."))

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'openid',
        }

        try:
            response = requests.post(url=requests_url, data=params, headers=headers)
            response = response.json()
            expires_in = response.get('expires_in')
            date_expiration = fields.Datetime.now() + timedelta(seconds=expires_in)
            self.env['ir.config_parameter'].sudo().set_param("cfr.cfr_access_token", response.get('access_token'))
            self.env['ir.config_parameter'].sudo().set_param("cfr.cfr_refresh_token", response.get('refresh_token'))
            self.env['ir.config_parameter'].sudo().set_param("cfr.date_expiration", date_expiration)
            _logger.info("===============END GENERATE TOKEN===============")

        except Exception as error:
            raise UserError(error) from error

    def regenerate_token(self):
        _logger.info("===============START REGENERATE TOKEN===============")
        client_id = self.env['ir.config_parameter'].sudo().get_param('cfr.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('cfr.client_secret')
        refresh_token = self.env['ir.config_parameter'].sudo().get_param('cfr.cfr_refresh_token')
        requests_url = self.env['ir.config_parameter'].sudo().get_param('cfr.base_url_token')

        if not client_id or not client_secret or not requests_url or not refresh_token:
            raise UserError(_("The token Generate service is not configured."))

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }

        try:
            response = requests.post(url=requests_url, data=params, headers=headers)
            if not response.status_code == 400:
                response = response.json()
                expires_in = response.get('expires_in')
                date_expiration = fields.Datetime.now() + timedelta(seconds=expires_in)
                self.env['ir.config_parameter'].sudo().set_param("cfr.cfr_access_token", response.get('access_token'))
                self.env['ir.config_parameter'].sudo().set_param("cfr.cfr_refresh_token", response.get('refresh_token'))
                self.env['ir.config_parameter'].sudo().set_param("cfr.date_expiration", date_expiration)
                _logger.info("===============END REGENERATE TOKEN===============")
            else:
                self.generate_token()
        except Exception as error:
            raise UserError(error) from error

    def send_mail_function(self, crf_doc_list_id):
        company_id = self.env.company
        template_id = self.env.ref('planification_cfr.email_template')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (crf_doc_list_id.id, crf_doc_list_id._name)
        if company_id and template_id:
            template_id.sudo().with_context(**dict(crf_doc_list_name=crf_doc_list_id.name, url=base_url)).send_mail(company_id.id, force_send=True)
