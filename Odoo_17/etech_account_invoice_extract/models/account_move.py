# -*- coding: utf-8 -*-

from odoo import models
from io import BytesIO
import base64
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = ['account.move']

    def _upload_to_extract(self):
        self.ensure_one()
        if self.is_invoice():
            attachment = self.message_main_attachment_id
            if attachment:
                files = {
                    'file': (
                        attachment.display_name,
                        BytesIO(base64.b64decode(attachment.datas)),
                        attachment.mimetype
                    )
                }
                try:
                    url = "https://invoice-run-nfej3ggfna-uc.a.run.app/generic"
                    result = requests.post(url, files=files)
                    result_content = json.loads(result.content)

                    if result.status_code == 200 and result_content.get('data'):
                        self.env['iap.account']._send_success_notification(
                            message=self._get_iap_bus_notification_success(),
                        )

                        self._save_form(result_content)

                except Exception as exception:
                    _logger.error('OCR Extract error: %s' % str(exception))
                    self.env['iap.account']._send_error_notification(
                        message=self._get_iap_bus_notification_error(),
                    )
                    return False

    def _save_form(self, ocr_results, force_write=False):
        print(ocr_results)
        datas = self._prepare_extracted_datas(ocr_results)
        with self._get_edi_creation() as move_form:
            print(move_form)
            move_form.ref = datas['ref']
            if "partner_id" in datas.keys():
                move_form.partner_id = datas['partner_id']
            if "date_order" in datas.keys():
                move_form.date_order = datas['date_order']
            move_form.invoice_line_ids = [(5, 0, 0)]
            move_form.invoice_line_ids = datas['result_line_ids']
            print(datas['ref'])

    def _prepare_extracted_datas(self, datas):
        print(datas)
        result = {}
        if len(datas['data']) > 0:
            # Recuperation de la reference de la facture
            if datas['data'][0]['id_facture']:
                result['ref'] = datas['data'][0]['id_facture']

            # Recuperation date de facturation facture
            if datas['data'][0]['date_order']:
                result['invoice_date'] = datas['data'][0]['date_order']

            # Recuperation partner de facturation facture
            if datas['data'][0]['fournisseur']:
                result['partner_id'] = self.env['res.partner'].search([('name', '=', datas['data'][0]['fournisseur'])], limit=1).id

            result['result_line_ids'] = []

            # Recuperation lignes de facturation facture
            for data in datas['data']:
                result['result_line_ids'].append((0,0, {
                    'product_id': self.env['product.product'].search([('name', '=', data['name'])], limit=1).id,
                    'quantity': data['product_uom_qty'],
                    'price_unit': data['price_unit'],
                    'currency_id': self.env['res.currency'].search([('name', '=', data['currency_id'])], limit=1).id
                }))
        return result
