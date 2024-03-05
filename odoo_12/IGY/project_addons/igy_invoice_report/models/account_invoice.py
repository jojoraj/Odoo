# -*- coding: utf-8 -*-

from odoo import models,fields

to_19_fr = (u'Zéro', 'Un', 'Deux', 'Trois', 'Quatre', 'Cinq', 'Six',
            'Sept', 'Huit', 'Neuf', 'Dix', 'Onze', 'Douze', 'Treize',
            'Quatorze', 'Quinze', 'Seize', 'Dix-sept', 'Dix-huit', 'Dix-neuf')
tens_fr = ('Vingt', 'Trente', 'Quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ('',
            'Mille', 'Millions', 'Milliards', 'Billions', 'Quadrillions',
            'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion',
            'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
            'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')


def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if val % 10:
                if dval == 70 or dval == 90:
                    amount = tens_fr[int(dval / 10 - 3)] + '-' + to_19_fr[int(val % 10 + 10)]
                    return amount
                else:
                    return dcap + '-' + to_19_fr[val % 10]
            return dcap


def _convert_nnn_fr(val):
    """ convert a value < 1000 to french

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = 'Cent'
        else:
            word = to_19_fr[rem] + ' Cent'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word


def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
        return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val and val < 1000000:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1:
                ret = denom_fr[didx]
            else:
                ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ' ' + french_number(r)
            return ret

        if dval > val and val > 1000000:
            mod = 1000 ** didx
            q = val // mod
            s = val - (q * mod)
            pet = _convert_nnn_fr(q) + ' ' + denom_fr[didx]
            if s > 0:
                pet = pet + ' ' + french_number(s)
            return pet


def amount_to_text_fr(numbers, currency):
    print(numbers)
    number = '%.2f' % numbers
    units_name = currency
    liste = str(number).split('.')
    print(abs(int(liste[0])))
    start_word = french_number(abs(int(liste[0])))
    end_word = french_number(int(liste[1]))
    cents_number = int(liste[1])
    if cents_number == 0:
        end_word = ''
        cents_name = ''
    else:
        cents_name = (cents_number > 1) and ' Centimes' or ' Centime'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result


to_19_en = (u'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six',
            'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen ',
            'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen')

tens_en = ('Twenty', 'Thirty', 'Fourty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety')

denom_en = ('',
            'Thousand ', 'Million', 'Milliard', 'Billions', 'Quadrillions',
            'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion',
            'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
            'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')


def _convert_nn_en(val):
    """ convert a value < 100 to English
    """
    if val < 20:
        return to_19_en[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_en)):
        if dval + 10 > val:
            if val % 10:
                if dval == 70 or dval == 90:
                    return tens_en[dval / 10 - 3] + '-' + to_19_en[val % 10 + 10]
                else:
                    return dcap + '-' + to_19_en[val % 10]
            return dcap


def _convert_nnn_en(val):
    """ convert a value < 1000 to English

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = 'One hundred'
        else:
            word = to_19_en[rem] + ' hundred'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_en(mod)
    return word


def english_number(val):
    if val < 100:
        return _convert_nn_en(val)
    if val < 1000:
        return _convert_nnn_en(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_en))):
        if dval > val and val < 1000000:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1:
                ret = denom_en[didx]
            else:
                ret = _convert_nnn_en(l) + ' ' + denom_en[didx]
            if r > 0:
                ret = ret + ', ' + english_number(r)
            return ret
        if dval > val and val > 1000000:
            mod = 1000 ** didx
            q = val // mod
            s = val - (q * mod)
            pet = _convert_nnn_en(q) + ' ' + denom_en[didx]
            if s > 0:
                pet = pet + ' ' + english_number(s)
            return pet


def amount_to_text_en(numbers, currency):
    number = '%.2f' % numbers
    units_name = currency
    liste = str(number).split('.')
    start_word = english_number(abs(int(liste[0])))
    end_word = english_number(int(liste[1]))
    cents_number = int(liste[1])
    if cents_number == 0:
        end_word = ''
        cents_name = ''
    else:
        cents_name = (cents_number > 1) and ' Cents' or ' Cent'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    note_igy = fields.Text(string="Note")
    description = fields.Char(string="Description")
    bc_source = fields.Char(string="Bon de commande source")
    amount_total_letter = fields.Char(string="Total en lettre", compute='_compute_amount_total_letter')

    def convert(self, number, currency_id):
        return amount_to_text_fr(number, currency_id)

    def _compute_amount_total_letter(self):
        for rec in self:
            if rec.amount_total:
                rec.amount_total_letter = rec.currency_id.amount_to_text(rec.amount_total)