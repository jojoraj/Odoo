odoo.define("evtc_front.evtc_appointment", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const EvtcMaps = require("evtc_front.reservations");
    var rpc = require("web.rpc");
    const dateSeparted = "/";
    const dateFormatOptions = "d m y";
    const current_default_datetime = new Date();
    const monthOfYears = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ];
    const abreviationOfMonths = [
        "Janv.",
        "Févr.",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juil.",
        "Août",
        "Sept.",
        "Oct.",
        "Nov.",
        "Déc.",
    ];
    const DayOfWeek = [
        "Dimanche",
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
    ];

    const abreviationOfDay = ["Dim.", "Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam."];

    const singleAbreviationOfDay = ["D", "L", "M", "M", "J", "V", "S"];

    const datePickerOptions = {
        dateFormat: "dd" + dateSeparted + "mm" + dateSeparted + "yy",
        minDate: current_default_datetime,
        closeText: "Fermer",
        prevText: "Précédent",
        nextText: "Suivant",
        currentText: "Aujourd'hui",
        monthNames: monthOfYears,
        monthNamesShort: abreviationOfMonths,
        dayNames: DayOfWeek,
        dayNamesShort: abreviationOfDay,
        dayNamesMin: singleAbreviationOfDay,
        weekHeader: "Sem.",
    };
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            "change #date": "_on_change_date",
            "click #change_recuperation_destination": "_on_click_change_recuperation",
            "click #change_destination": "_on_click_change_destination",
            "click #evtc_appointment_button": "_on_click_appoitment_button",
            "change #customRadio1, #customRadio2": "_on_change_custom_button",
            "change #time": "change_time_today",
            "focusout #time": "change_time_today",
            "click #timeselector-div": "change_time_today",
            "click .timeselector-value": "change_time_today",
        }),
        start: async function () {
            await this._super.apply(this, arguments);
            await this._on_change_custom_button();
            $("#date")
                .datepicker(datePickerOptions)
                .datepicker("setDate", current_default_datetime);
            $("#time").timeselector({
                step: 15,
                hours12: false,
            });
            this._time_initialisation(true, current_default_datetime);
            this.change_date_name();
            const footers = $(this.el).find(".oe_recup_res");
            if (footers[0]) {
                footers.attr("style", "");
            }
        },
        _on_change_date: function () {
            this.change_date_name();
            this.change_time_today();
        },

        _convert_datetime_to_string: function (date = new Date()) {
            const day = date.getUTCDate();
            const month = date.getMonth() + 1;
            const year = date.getUTCFullYear();
            return {
                days: day,
                months: month,
                years: year,
                dayFormatedY: year + dateSeparted + month + dateSeparted + day,
                dayFormatedD: day + dateSeparted + month + dateSeparted + year,
            };
        },
        _get_zfill: function (x) {
            return x.toString().length > 1 ? x : "0" + x;
        },

        revertDateString: function (date) {
            let vals;
            const nextDate = current_default_datetime;
            const current_day = this._get_formated_datetime(nextDate);
            const tomorrow_day = this._get_formated_datetime(
                new Date(nextDate.setDate(nextDate.getDate() + 1))
            );
            const next_tomorrow_day = this._get_formated_datetime(
                new Date(nextDate.setDate(nextDate.getDate() + 1))
            );
            if (date === "Aujourd'hui") {
                vals = current_day
            } else if (date === "Demain") {
                vals = tomorrow_day
            } else if (date === 'Après demain') {
                vals = next_tomorrow_day
            }
            return vals ? vals.formatedDate : date;
        },

        _get_formated_datetime: function (datetime, times = "00:00") {
            let dateList = ["Aujourd'hui", "Demain", "Après demain"];
            if (dateList.includes(datetime)) {
                datetime = this.revertDateString(datetime)
            }
            const arrayDatetime = dateFormatOptions.split(" ");
            const daysIndex = arrayDatetime.indexOf("d");
            const monthIndex = arrayDatetime.indexOf("m");
            const yearsIndex = arrayDatetime.indexOf("y");
            if (typeof datetime === "object") {
                const d = this._convert_datetime_to_string(datetime);
                datetime = daysIndex === 0 ? d.dayFormatedD : d.dayFormatedY;
            }
            const splited = datetime.split(dateSeparted);
            const dd = this._get_zfill(splited[daysIndex]);
            const mm = this._get_zfill(splited[monthIndex]);
            const yy = this._get_zfill(splited[yearsIndex]);
            const hm = times.split(":");
            const formatD = dd + dateSeparted + mm + dateSeparted + yy;
            const formatY = yy + dateSeparted + mm + dateSeparted + dd;
            return {
                days: dd,
                month: mm,
                years: yy,
                hours: hm[0],
                minutes: hm[1],
                formatedDate: formatD,
                formatedDatewithYear: formatY,
                formatedDateTimeD: formatD + " " + times,
                formatedDateTimeY: formatY + " " + times,
            };
        },

        change_date_name: function () {
            const myDate = this._get_formated_datetime($("#date").val());
            const nextDate = new Date();
            const current_day = this._get_formated_datetime(nextDate);
            const tomorrow_day = this._get_formated_datetime(
                new Date(nextDate.setDate(nextDate.getDate() + 1))
            );
            const next_tomorrow_day = this._get_formated_datetime(
                new Date(nextDate.setDate(nextDate.getDate() + 1))
            );
            let day_name;
            switch (myDate.formatedDate) {
                case current_day.formatedDate:
                    day_name = "Aujourd'hui";
                    break;
                case tomorrow_day.formatedDate:
                    day_name = "Demain";
                    break;
                case next_tomorrow_day.formatedDate:
                    day_name = "Après demain";
                    break;
            }
            $("#date").datepicker("setDate", new Date(myDate.formatedDatewithYear));
            if (day_name) {
                $("#date").val(day_name);
            }
        },
        _time_initialisation: function (is_initialisation, date) {
            date.setHours(date.getHours() + 1);
            const defaultHours =
                String(date.getHours()).length > 1 ? date.getHours() : "0" + date.getHours();
            let defaultMinutes =
                String(date.getMinutes()).length > 1 ?
                    date.getMinutes() :
                    "0" + date.getMinutes();
            if (defaultMinutes === "00") {
                defaultMinutes = "00";
            } else if (parseInt(defaultMinutes) > 1 && parseInt(defaultMinutes) <= 15) {
                defaultMinutes = "00";
            } else if (parseInt(defaultMinutes) > 15 && parseInt(defaultMinutes) <= 30) {
                defaultMinutes = "15";
            } else if (parseInt(defaultMinutes) > 30 && parseInt(defaultMinutes) <= 45) {
                defaultMinutes = "30";
            } else if (parseInt(defaultMinutes) > 45 && parseInt(defaultMinutes) <= 59) {
                defaultMinutes = "45";
            }
            if (is_initialisation) {
                const newDate = new Date();
                if (parseInt(newDate.getHours()) === 23) {
                    $("#time").attr("value", defaultHours + ":" + defaultMinutes);
                    $("#date").val("Demain");
                } else {
                    $("#time").attr("value", defaultHours + ":" + defaultMinutes);
                }
            } else {
                const time = $("#time").val();
                const hours = parseInt(date.getHours());
                const minutes = parseInt(date.getMinutes());
                const val_split = time.split(":");
                const hours_val = parseInt(val_split[0]);
                const minute_val = parseInt(val_split[1]);
                if (
                    hours > hours_val ||
                    (hours === hours_val && minutes > minute_val) ||
                    hours === 0
                ) {
                    $("#time").val(defaultHours + ":" + defaultMinutes);
                }
                if (hours === 0) {
                    $("#date").val("Demain");
                }
            }
        },
        change_time_today: function () {
            const self = this;
            setTimeout(function () {
                const date = new Date();
                const time = $("#time").val();
                const val_split = time.split(":");
                const hours_val = parseInt(val_split[0]);
                if ($("#date").val() === "Aujourd'hui") {
                    self._time_initialisation(false, date);
                } else if (
                    $("#date").val() === "Demain" &&
                    parseInt(date.getHours()) === 23 &&
                    hours_val === 0
                ) {
                    date.setHours(date.getHours() + 1);
                    const defaultHours =
                        String(date.getHours()).length > 1 ?
                            date.getHours() :
                            "0" + date.getHours();
                    let defaultMinutes =
                        String(date.getMinutes()).length > 1 ?
                            date.getMinutes() :
                            "0" + date.getMinutes();
                    if (defaultMinutes === "00") {
                        defaultMinutes = "00";
                    } else if (parseInt(defaultMinutes) > 1 && parseInt(defaultMinutes) <= 15) {
                        defaultMinutes = "00";
                    } else if (parseInt(defaultMinutes) > 15 && parseInt(defaultMinutes) <= 30) {
                        defaultMinutes = "15";
                    } else if (parseInt(defaultMinutes) > 30 && parseInt(defaultMinutes) <= 45) {
                        defaultMinutes = "30";
                    } else if (parseInt(defaultMinutes) > 45 && parseInt(defaultMinutes) <= 59) {
                        defaultMinutes = "45";
                    }
                    $("#time").val(defaultHours + ":" + defaultMinutes);
                }
            }, 500);
        },
        _on_click_change_recuperation: function () {
            this.appointment.addClass("d-none");
            this.recuperation.removeClass("d-none");
        },
        _on_click_change_destination: function () {
            this.appointment.addClass("d-none");
            this.destination.removeClass("d-none");
        },
        _on_click_appoitment_button: async function (events) {
            const isNow = this.customRadioNow.is(":checked");
            let reservationDateTime = this._getAppoitmentDatetime(isNow);
            await rpc
                .query({
                    model: "fleet.vehicle.model.category",
                    method: "get_vehicle_price_per_km",
                    args: [],
                    kwargs: {recuperation: reservationDateTime},
                })
                .then((result) => {
                    for (let vehicle_id in result) {
                        let found_html_id = $("#vehicle_" + vehicle_id);
                        let price = result[vehicle_id];
                        if (found_html_id.length > 0) {
                            found_html_id[0].innerHTML = price + " Ar / Km";
                        }
                    }
                });
            this.recuperation_adress_heading_appointment.contents().eq(4).remove();
            this.recuperation_adress_appointment.after(this.address_recuperation.val());
            this.destination_adress_heading_appointment.contents().eq(4).remove();
            this.destination_adress_appointment.after(this.address_destination.val());
            this.time_heading_appointment.contents().eq(2).remove();
            this.time_appointment.after(this.get_appointment_time());
            this.appointment.addClass("d-none");
            this.vehicle.removeClass("d-none");
            // $("#evtc_aside").animate({ scrollTop: $('#evtc_aside').height() });
            $("#evtc_aside").animate({scrollTop: $("#vehicle").position().top});
            this._computeAutoClass(events, 'evtc_appointment', 'evtc_appointment_button', reservationDateTime, '', '')
        },

        get_appointment_time: function () {
            const calendar = $("#date");
            const time = $("#time");
            const customRadioNow = $("#customRadio1");
            const customRadioSet = $("#customRadio2");
            if (customRadioNow.is(":checked")) {
                return this.get_time_now_thirty;
            } else if (customRadioSet.is(":checked")) {
                // Return date.getFullYear()+"-"+(date.getMonth()+ 1)+"-"+date.getDate()+" "+date.getHours()+":"+date.getMinutes();
                // let date = new Date(time.val());
                // calendar.val(date.getFullYear()+"-"+(date.getMonth()+ 1) +"-"+ date.getDate());
                return calendar.val() + " " + time.val();
            }
        },
        get_time_now_thirty: function () {
            const today = new Date();
            const todayHour = today.getHours();
            const todayMinute = today.getMinutes();
            const todayThirty = new Date(today.getTime() + 30 * 60 * 1000);
            const hour =
                String(todayThirty.getHours()).length === 2 ?
                    todayThirty.getHours() :
                    "0" + todayThirty.getHours();
            const minute =
                String(todayThirty.getMinutes()).length === 2 ?
                    todayThirty.getMinutes() :
                    "0" + todayThirty.getMinutes();
            // Return 'Aujourd\'hui ' + today.getHours() + ':' + (today.getMinutes()) + ':' + today.getSeconds()
            if (parseInt(todayHour) < 23) {
                return "Aujourd'hui " + hour + ":" + minute;
            } else if (parseInt(todayHour) === 23) {
                return parseInt(todayMinute) < 30 ?
                    "Aujourd'hui " + hour + ":" + minute :
                    "Demain " + hour + ":" + minute;
            }
            return null;
        },
        _on_change_custom_button: function () {
            if (this.customRadioNow.is(":checked")) {
                this.time_selection.hide();
                this.waiting.show();
                this.waiting_label.show();
            }
            if (this.customRadioSet.is(":checked")) {
                this.time_selection.show();
                this.waiting.hide();
                this.waiting_label.hide();
            }
            return true;
        },
    });
});
