odoo.define('evtc_location.evtc_recuperation_long', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    publicWidget.registry.recuperationLongWidget = publicWidget.Widget.extend({
        selector: '.long-duration',
        events: {
            'keyup #address_recuperation': '_check_input_recuperation',
            'keydown #address_recuperation': '_on_keydown_change_input',
            'change #address_recuperation': '_on_keydown_change_input',
            'focusout #address_recuperation': '_on_focusout_input',
            'click #evtc_recuperation_button_long': '_on_click_recuperation_button',
            'click .li-street-recuperation': '_on_click_street_recuperation'
        },
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            this.address_recuperation = $('#address_recuperation');
            this.div_recuperation = $('#evtc-form-recuperation');
            this.recuperation_adress_heading = $('#recuperation_adress_heading_appointment');
            this.recuperation_adress = $('#recuperation_adress_appointment');
            this.recuperation = $('#evtc_recuperation');
            this.vehicle = $('#evtc_vehicle');
            this.real_address_recovery = $('#real_address_recovery');
            this.real_address_recovery.val('');
            return Promise.all(defs);
        },
        _check_input_recuperation: function() {
            if (!this.address_recuperation.val()) {
                this.div_recuperation.siblings('small').remove();
                this.div_recuperation.after('<small class="text-danger">Veuillez remplir le champs</small>');
                this.address_recuperation.css('border-color', 'red')
            } else {
                this.div_recuperation.siblings('small').remove();
                this.address_recuperation.css('border-color', 'black');
            }
        },
        _on_keydown_change_input: function() {
            this._check_input_recuperation();
            this._auto_complete_recuperation();
        },
        _on_focusout_input: function() {
            this._check_input_recuperation();
            this._on_recuperation_focusout();
        },
        _auto_complete_recuperation: function() {
            if (!this.address_recuperation.val()) {
                $('.paragraph_adress_recuperation').show();
                $('.list-group-adress-recuperation').show();
            } else {
                $('.paragraph_adress_recuperation').hide();
                $('.list-group-adress-recuperation').hide();
            }
        },
        _on_recuperation_focusout: function() {
            $('.paragraph_adress_recuperation').show();
            $('.list-group-adress-recuperation').show();
        },
        _on_click_street_recuperation: function(e) {
            this.address_recuperation.val(e.target.innerText);
            const attributes = e.currentTarget.attributes
            const street = attributes['data-street']
            this.real_address_recovery.val(street.value)
            this._check_input_recuperation();
        },
        _on_click_recuperation_button: function() {
            if (!this.address_recuperation.val()) {
                this.div_recuperation.siblings('small').remove();
                this.div_recuperation.after('<small class="text-danger">Veuillez remplir le champs</small>');
                this.address_recuperation.css('border-color', 'red')
            } else {
                rpc.query({
                    route: '/evtc/save_address',
                    params: {
                        'street': this.address_recuperation.val(),
                        'latitude': $('#latitude_address_recovery').val(),
                        'longitude': $('#longitude_address_recovery').val(),
                        'is_historical': true
                    },
                })
                this.recuperation_adress_heading.contents().eq(4).remove();
                this.recuperation_adress.after(this.address_recuperation.val());
                this.div_recuperation.siblings('small').remove();
                this.address_recuperation.css('border-color', 'black');
                this.recuperation.addClass('d-none');
                this.vehicle.removeClass('d-none');
            }
        }
    });
    return {
        recuperationLongWidget: publicWidget.registry.recuperationLongWidget
    };
})
