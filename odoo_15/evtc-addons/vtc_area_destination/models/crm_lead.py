import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class LeadCrm(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create_crm_lead(self, lead):
        others_destination = lead.get('others_destination', [])
        if others_destination:
            del lead['others_destination']
            del lead['as_many_course']
        record = super(LeadCrm, self).create_crm_lead(lead)
        if isinstance(record, int):
            record = self.env['crm.lead'].browse(record).exists()
        record = record.sudo()
        crm_lead_course = self.env['crm.lead.course'].sudo()
        for course in others_destination:
            course.update({
                'lead_id': record.id,
                'kilometers_estimted': self.convert_real_km_float(
                    course.get('kilometers_estimted', 0)
                )
            })
            course_id = crm_lead_course.create(course)
            record.others_destination += course_id
        if record.others_destination:
            record.as_many_course = True
        return record.id

    def convert_real_km_float(self, km):
        xkm_trip = 0
        if km and ' ' in km:
            splited_km = km.split(' ')
            if splited_km[1].strip() == 'km':
                xkm_trip += float(splited_km[0].replace(',', '.') if ',' in splited_km[0] else splited_km[0])
        return xkm_trip
