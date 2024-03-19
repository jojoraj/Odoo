odoo.define('evtc_front._addMore.Partner', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.websitePortal = publicWidget.Widget.extend({
        selector: '.oe_partner_country',
        events: {
            'click .custom-control-label': '_onShowEvent',
            'change #own_country': '_ChangeSelection',
        },
        _onShowEvent: function () {
            const country = $('#oe_county_select');
            const current_country = $('#own_country').val();
            const yes = $("#customRadio11").is(':checked');
            const no = $("#customRadio10").is(':checked');
            const email = $('.add_email');
            this.$div = $(this.el).find('.oe_partner_country')
            if (no) {
                $('input#name').removeAttr('disabled')
                $('input#name').css('background-color','#FFFFFF')
                $('select#own_country').removeAttr('disabled')
                $('#s2id_own_country').attr('style','background-color: #FFFFFF !important')
                $('.remove-background').css('background-color','#FFFFFF')
                $('input#tel').removeAttr('disabled')
                $('input#tel').css('background-color','#FFFFFF')
                $('label#for-tel').innerText = "Son numéro *"
                country.show();
                if (current_country !== 'MG') {
                    email.show();
                } else {
                    email.hide()
                }
            }
            if (yes) {
                $('input#name').attr('disabled','disabled')
                $('input#name').css('background-color','#f1f1f1')
                // #f1f1f1, FFFFFF
                $('#s2id_own_country').attr('style','background-color: #f1f1f1 !important')
                $('select#own_country').attr('disabled','disabled')
                $('input#tel').attr('disabled','disabled')
                $('input#tel').css('background-color','#f1f1f1')
                $('label#for-tel').innerText = "Mon numéro *"
                country.hide();
                email.hide();
                $('.small-constrains').empty();
            }
        },
        _ChangeSelection: function (Z) {
            const value = Z.currentTarget.value;
            const email_ = $('.add_email');
            if (value !== 'MG') {
                email_.show();
            } else {
                email_.hide();
            }
        }
    });

})
