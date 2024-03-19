import logging

import phonenumbers
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


def format_phone_number(phone_number, country):
    try:
        phone_number = str(phonenumbers.parse(phone_number).national_number)
    except Exception as e:
        _logger.info('phone_number not formatted : {}'.format(e))

    return phone_validation.phone_format(
        phone_number,
        country.code if country else None,
        country.phone_code if country else None,
        force_format='INTERNATIONAL',
        raise_exception=True
    )
