odoo.define("evtc_front.evtc_destination", function(require) {
    "use strict";

    var rpc = require("web.rpc");
    const EvtcMaps = require("evtc_front.reservations");
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            "keyup #address_destination": "_check_input_destination",
            "keydown #address_destination": "_on_keydown_destination",
            "change #address_destination": "_on_keydown_destination",
            "focusout #address_destination": "_on_focusout_destination",
            "click .register-destination-adress": "_onClickStreetDestinationAdress",
        }),
        start: async function() {
            await this._super.apply(this, arguments);
            this.destination_address_destination.val("");
        },
        _on_keydown_destination: function() {
            this._check_input_destination();
            this._on_complete_destination();
        },
        _on_focusout_destination: function() {
            this._check_input_destination();
            this._on_destination_focusout();
        },
        _check_input_destination: function() {
            if (!this.address_destination.val()) {
                this.div_destination.siblings("small").remove();
                this.div_destination.after(
                    '<small class="text-danger">Veuillez remplir le champs</small>'
                );
                this.address_destination.css("border-color", "red");
            } else {
                this.div_destination.siblings("small").remove();
                this.address_destination.css("border-color", "black");
            }
        },
        _on_complete_destination: function() {
            if (!this.address_destination.val()) {
                $(".paragraph_adress_destination").show();
                $(".list-group-adress-destination").show();
                $("#evtc_destination_button").removeClass("resume_class");
            } else {
                $(".paragraph_adress_destination").hide();
                $(".list-group-adress-destination").hide();
                $("#evtc_destination_button").addClass("resume_class");
            }
        },
        _on_destination_focusout: function() {
            $(".paragraph_adress_destination").show();
            $(".list-group-adress-destination").show();
            $("#evtc_destination_button").removeClass("resume_class");
        },
        _onChangePickUpZoneStep: function() {
            this.destination.addClass("d-none");
            this.recuperation.removeClass("d-none");
            this._stepByPickupZone();
        },
        _onClickStreetDestinationAdress: async function(e) {
            this.address_destination.val(e.target.innerText);
            const attribute = e.currentTarget.attributes;
            const street = attribute["data-street"];
            this.destination_address_destination.val(street.value);
            this._check_input_destination();
        },
        _set_draggable_marker_destination: async function(events) {
            await this._super.apply(this, arguments)
            this._onClickDestinationButton(events)
        },
        _onClickDestinationButton: function(events) {
            if (!this.address_destination.val()) {
                this.div_destination.siblings("small").remove();
                this.div_destination.after(
                    '<small class="text-danger">Veuillez remplir le champs</small>'
                );
                this.address_destination.css("border-color", "red");
            } else {
                rpc.query({
                    route: "/evtc/save_address",
                    params: {
                        street: this.address_destination.val(),
                        latitude: $("#latitude_address_destination").val(),
                        longitude: $("#longitude_address_destination").val(),
                        is_historical: true,
                    },
                });
                this.recuperation_adress_heading_destination.contents().eq(4).remove();
                this.recuperation_adress_destination.after(this.address_recuperation.val());
                this.destination_adress_heading.contents().eq(4).remove();
                this.destination_adress.after(this.address_destination.val());
                this.div_destination.siblings("small").remove();
                this.address_destination.css("border-color", "black");
                this.destination.addClass("d-none");
                this.appointment.removeClass("d-none");
                // $("#evtc_aside").animate({ scrollTop: $('#evtc_aside').height() });
                $("#evtc_aside").animate({ scrollTop: $("#when").position().top });

                let lng = $("#longitude_address_destination").val();
                let lat = $("#latitude_address_destination").val();
                let values = this.address_destination.val()
                this._computeAutoClass(events, 'evtc_destination', 'evtc_destination_button', values, lat, lng)
            }
        },
    });
});
