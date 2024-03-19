# -*- coding: utf-8 -*-
from odoo import _

PICKUP_FIELDS = ['pick_up_lat', 'pick_up_long', 'pick_up_zone']
DEST_FIELDS_WITH = ['latitude', 'longitude', 'name']
DEST_FIELDS_WITHOUT = ['dest_lat', 'dest_long', 'destination_zone']
FIELDS_REC = ['latitude', 'longitude', 'description']
TRIP_REQUEST = {
    "clientPhone": "",
    "driverPhone": "",
    "immatriculationID": "",
    "siid": "",
    "locations": [],
    "odometer": 0,
    "dateCreated": ""
}


def fields_strip_values(self, fields):
    location = {}
    for index, record in enumerate(fields):
        types = float if index < 2 else str
        convert_vals = self[record] and types(self[record]) or self[record]
        location[FIELDS_REC[index]] = convert_vals
    return location

def compact_fields():
    return dict(
        pickup=PICKUP_FIELDS,
        dest_without=DEST_FIELDS_WITHOUT,
        dest_with=DEST_FIELDS_WITH,
        trip_body=TRIP_REQUEST
    )

http_error = {
    400: {
        'code': 400,
        'message': ''
    }
}

def http_errors(code, mess):
    response = http_error[code]
    response['message'] = mess
    return response
