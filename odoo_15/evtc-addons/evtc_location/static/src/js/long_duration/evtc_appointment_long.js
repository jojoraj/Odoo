odoo.define('evtc_location.evtc_appointment_long', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const packageWidget = require('evtc_location.package_template_long').package;
    const vehicleLongWidget = require('evtc_location.vehicle_template_long').vehicleLongWidget;

    const dateSeparted = '/'
    const dateFormatOptions = 'd m y'
    const current_default_datetime = new Date();
    const monthOfYears = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre',
        'Octobre', 'Novembre', 'Décembre'
    ]
    const abreviationOfMonths = [
        'Janv.', 'Févr.', 'Mars', 'Avril', 'Mai', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.'
    ]
    const DayOfWeek = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

    const abreviationOfDay = ['Dim.', 'Lun.', 'Mar.', 'Mer.', 'Jeu.', 'Ven.', 'Sam.']

    const singleAbreviationOfDay = ['D', 'L', 'M', 'M', 'J', 'V', 'S']

    const datePickerOptions = {
        dateFormat: 'dd' + dateSeparted + 'mm' + dateSeparted + 'yy',
        minDate: current_default_datetime,
        closeText: 'Fermer',
        prevText: 'Précédent',
        nextText: 'Suivant',
        currentText: "Aujourd'hui",
        monthNames: monthOfYears,
        monthNamesShort: abreviationOfMonths,
        dayNames: DayOfWeek,
        dayNamesShort: abreviationOfDay,
        dayNamesMin: singleAbreviationOfDay,
        weekHeader: 'Sem.',
    }

    const myDate = new Date()
    myDate.setHours(myDate.getHours() + 1);

    publicWidget.registry.appointementLongWidget = publicWidget.Widget.extend({
        selector: '.long-duration',
        events: {
            'change #date, #date_end, #time': 'change_time_today',
            'click #evtc_appointment_button_long': '_on_click_appoitment_button',
            'focusout #time': 'change_time_today',
        },
        start: async function () {
            await Promise.all([this._super.apply(this, arguments)]);
            this.appointment = $('#evtc_appointment');
            this.recuperation = $('#evtc_recuperation');
            this.recuperation_adress_heading_appointment = $('#recuperation_adress_heading_destination');
            this.recuperation_adress_appointment = $('#recuperation_adress_destination');
            this.time_appointment = $('#time_appointment');
            this.vehicle = $('#evtc_vehicle');
            this.address_recuperation = $('#address_recuperation');
            this.payement_resume = $('#evtc_payement_resume');
            this.package = $('#evtc_package');
            this.choise_vehicle_heading = $('#resume_choise_vehicle_heading_appointment');
            this.choise_vehicle = $('#choise_vehicle');
            this.time_heading_appointment = $('#time_heading_appointment_resume');

            this.address_recuperation.val('');
            $('.details_run').val('');

            $('#date, #date_end').datepicker(datePickerOptions).datepicker('setDate', current_default_datetime);
            $('#time, #time_end').timeselector({
                step: 15,
                hours12: false
            });
            this._reinitialized_current_time()
        },

        _reinitialized_current_time: function () {
            const currentTime = new Date();
            const defaultHours = String((myDate.getHours())).length > 1 ?
                (myDate.getHours()) : "0" + (myDate.getHours());
            const defaultMinutes = String(currentTime.getMinutes()).length > 1 ?
                currentTime.getMinutes() : "0" + currentTime.getMinutes();
            $('#time').val(defaultHours + ":" + defaultMinutes);
        },

        _get_formated_datetime: function (datetime, times) {
            const splited = datetime.split(dateSeparted)
            const arrayDatetime = dateFormatOptions.split(' ')
            const daysIndex = arrayDatetime.indexOf('d')
            const monthIndex = arrayDatetime.indexOf('m')
            const yearsIndex = arrayDatetime.indexOf('y')
            const hm = times.split(':')
            const formatD = splited[daysIndex] + dateSeparted + splited[monthIndex] + dateSeparted + splited[yearsIndex]
            const formatY = splited[yearsIndex] + dateSeparted + splited[monthIndex] + dateSeparted + splited[daysIndex]
            return {
                days: splited[daysIndex],
                month: splited[monthIndex],
                years: splited[yearsIndex],
                hours: hm[0],
                minutes: hm[1],
                formatedDate: formatD,
                formatedDatewithYear: formatY,
                formatedDateTimeD: formatD + ' ' + times,
                formatedDateTimeY: formatY + ' ' + times,
            }
        },

        _add_hours: function (numOfHours = 0, numOfMinutes = 0, date = new Date()) {
            date.setTime(date.getTime() + 60000 * (numOfHours * 60 + numOfMinutes));
            return date;
        },

        _get_all_dates: function (d = new Date()) {
            const mont = (d.getMonth() + 1) % 12
            const dd = d.getDate().toString().length > 1 ? d.getDate() : '0' + d.getDate()
            const mm = mont.toString().length > 1 ? mont : '0' + mont
            return {
                day: d.getDate(),
                month: d.getMonth(),
                year: d.getYear(),
                hours: d.getHours().toString().length > 1 ? d.getHours() : '0' + d.getHours(),
                minutes: d.getMinutes().toString().length > 1 ? d.getMinutes() : '0' + d.getMinutes(),
                default: dd + dateSeparted + mm + dateSeparted + d.getFullYear(),
            }
        },

        _onchange_time_end: async function () {
            const appropriates = this._get_formated_datetime($('#date').val(), $('#time').val())
            const appropriatesFormatDate = new Date(appropriates.formatedDateTimeY)
            const duration = $('#choose_rate').find("input[type=radio]:checked").data('hour');
            const approvalFormatWithDate = this._add_hours(parseInt(duration), 0, appropriatesFormatDate)
            const newEndDate = this._get_all_dates(approvalFormatWithDate)
            let withChange = true
            const nowDay = this._get_all_dates(myDate)
            const appropriate_hours = appropriates.hours === nowDay.hours && appropriates.minutes < nowDay.minutes
            const appropriate_less_hours = appropriates.hours < nowDay.hours
            if (nowDay.default === appropriates.formatedDate && (appropriate_less_hours  || appropriate_hours) ){
                withChange = false
            }
            return {
                abstractDate: approvalFormatWithDate,
                timers: newEndDate.hours + ':' + newEndDate.minutes,
                withChange: withChange,
            }
        },

        change_time_today: function (x = 500) {
            const self = this
            setTimeout(function () {
                self._onchange_time_end().then(resultOject => {
                    if (resultOject.withChange){
                        $('#time_end').val(resultOject.timers);
                        $('#date_end').datepicker('setDate', resultOject.abstractDate);
                    } else {
                        self._reinitialized_current_time()
                    }
                })
            }, x)
        },

        reformat_date_time: function (date, time) {
            return date + " à " + time;
        },

        get_appointment_time: function () {
            const date_start = $('#date').val();
            const time_start = $('#time').val();
            const date_end = $('#date_end').val();
            const time_end = $('#time_end').val();
            const details = $('.details_run').val();

            $('#start').text('Début: ' + this.reformat_date_time(date_start, time_start))
            $('#end').text('Fin: ' + this.reformat_date_time(date_end, time_end))
            $('#details_value').text('Détails: ' + details)
        },

        _on_click_appoitment_button: function () {

            this.recuperation_adress_heading_appointment.contents().eq(4).remove();
            this.recuperation_adress_appointment.after(this.address_recuperation.val());
            this.choise_vehicle_heading.contents().eq(2).remove();
            this.choise_vehicle_heading.find('span').after(vehicleLongWidget.prototype.choosing_vehicle());
            this.time_heading_appointment.contents().eq(2).remove();
            $('.resume-price').contents().eq(2).remove();
            this.time_heading_appointment.find('span').after(packageWidget.prototype.choosing_rate_hour());
            this.time_heading_appointment.find('i').after(packageWidget.prototype.choosing_rate_price());
            this.time_heading_appointment.contents().eq(4).remove();
            this.get_appointment_time();
            this.appointment.addClass('d-none');
            this.payement_resume.removeClass('d-none');
        },

    });
    return {
        appointementLongWidget: publicWidget.registry.appointementLongWidget
    }
});
