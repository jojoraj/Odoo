odoo.define('evtc_location.package_template_long', function(require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var vehicleLongWidget = require('evtc_location.vehicle_template_long').vehicleLongWidget;

    publicWidget.registry.packageLongWidget = publicWidget.Widget.extend({
        selector: '.long-duration',
        events: {
            'click #evtc_package_button_long': '_on_click_package_button'
        },
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            this.vehicle = $('#evtc_vehicle');
            this.recuperation = $('#evtc_recuperation');
            this.appointment = $('#evtc_appointment');
            this.recuperation_adress_heading_vehicle = $('#recuperation_adress_heading_vehicle_appointment');
            this.recuperation_adress_vehicle = $('#recuperation_adress_vehicle');
            this.address_recuperation = $('#address_recuperation');
            this.choise_vehicle_heading = $('#choise_vehicle_heading_appointment');
            this.choise_vehicle = $('#choise_vehicle');
            this.package = $('#evtc_package');
            return Promise.all(defs);
        },

        choosing_rate_hour: function(ev) {
            var form_choose = $('#choose_rate');
            const hour = form_choose.find("input[type=radio]:checked").data('hour');
            return ' ' + hour + ' h';
        },

        choosing_rate_price: function(ev) {
            var form_choose = $('#choose_rate');
            const price = form_choose.find("input[type=radio]:checked").data('price');
            return price.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' Ar';
        },

        _time_initialisation_end: function() {
            const dateNow = new Date();
            const getHour = dateNow.getHours();
            const getMinute = dateNow.getMinutes();
            const duration = $('#choose_rate').find("input[type=radio]:checked").data('hour');

            var defaultHours = parseInt(getHour) + parseInt(duration);
            var defaultMinutes = getMinute;
            var number_day = Math.floor(defaultHours / 24);
            var reset = defaultHours % 24


            defaultHours = String(defaultHours).length === 2 ? defaultHours : "0" + (defaultHours);
            defaultMinutes = String(defaultMinutes).length === 2 ? defaultMinutes : "0" + defaultMinutes;
            reset = String(reset).length === 2 ? reset : "0" + reset;
            if (defaultMinutes === "00") {
                defaultMinutes = "00";
            } else if (parseInt(defaultMinutes) > 1 && parseInt(defaultMinutes) <= 15) {
                defaultMinutes = "15"
            } else if (parseInt(defaultMinutes) > 15 && parseInt(defaultMinutes) <= 30) {
                defaultMinutes = "30"
            } else if (parseInt(defaultMinutes) > 30 && parseInt(defaultMinutes) <= 45) {
                defaultMinutes = "45"
            } else if (parseInt(defaultMinutes) > 45 && parseInt(defaultMinutes) <= 59) {
                defaultMinutes = "00";
                defaultHours += 1;
            }
            if (number_day === 0) {
                $('#time_end').val(defaultHours + ":" + defaultMinutes);
                $('#date_end').datepicker('setDate', new Date());
            } else {
                $('#time_end').val(reset + ":" + defaultMinutes);
                $('#date_end').datepicker('setDate', number_day);
            }
        },

        _on_click_package_button: async function() {
            this.recuperation_adress_heading_vehicle.contents().eq(4).remove();
            this.recuperation_adress_heading_vehicle.find('i').after(this.address_recuperation.val());
            this.choise_vehicle_heading.contents().eq(2).remove();
            this.choise_vehicle_heading.find('span').after(vehicleLongWidget.prototype.choosing_vehicle());
            $('#time_heading_appointment').contents().eq(2).remove();
            $('#rate').contents().eq(2).remove();
            $('#time_heading_appointment').find('span').after(this.choosing_rate_hour());
            $('#time_heading_appointment').find('i').after(this.choosing_rate_price());
            $('#time_heading_appointment').contents().eq(4).remove();
            await this._time_initialisation_end();
            this.package.addClass('d-none');
            this.appointment.removeClass('d-none');
        },

    })
    return {
        package: publicWidget.registry.packageLongWidget
    };
})
