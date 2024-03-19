odoo.define("evtc_front.evtc_recuperation", function (require) {
    "use strict";

    var rpc = require("web.rpc");
    const EvtcMaps = require("evtc_front.reservations");
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            "keyup #address_recuperation": "_check_input_recuperation",
            "keydown #address_recuperation": "_on_keydown_change_input",
            "change #address_recuperation": "_on_keydown_change_input",
            "focusout #address_recuperation": "_on_focusout_input",
            "click .register-recuperation-adress": "_onClickStreetPickUpZone",
        }),

        start: async function () {
            await this._super.apply(this, arguments);
            this.real_address_recovery.val("");
        },
        _check_input_recuperation: function () {
            if (!this.address_recuperation.val()) {
                this.div_recuperation.siblings("small").remove();
                this.div_recuperation.after(
                    '<small class="text-danger">Veuillez remplir le champs</small>'
                );
                this.address_recuperation.css("border-color", "red");
            } else {
                this.div_recuperation.siblings("small").remove();
                this.address_recuperation.css("border-color", "black");
            }
        },
        _on_keydown_change_input: function () {
            this._check_input_recuperation();
            this._auto_complete_recuperation();
        },
        _on_focusout_input: function () {
            this._check_input_recuperation();
            this._on_recuperation_focusout();
        },
        _auto_complete_recuperation: function () {
            if (!this.address_recuperation.val()) {
                $(".paragraph_adress_recuperation").show();
                $(".list-group-adress-recuperation").show();
                // $('#evtc_recuperation_button').removeClass('resume_class')
            } else {
                $(".paragraph_adress_recuperation").hide();
                $(".list-group-adress-recuperation").hide();
                // $('#evtc_recuperation_button').addClass('resume_class')
            }
            // This._on_recuperation_focusout();
        },
        _on_recuperation_focusout: function () {
            $(".paragraph_adress_recuperation").show();
            $(".list-group-adress-recuperation").show();
            // $('#evtc_recuperation_button').removeClass('resume_class')
        },
        _onClickStreetPickUpZone: function (e) {
            this.address_recuperation.val(e.target.innerText);
            const attributes = e.currentTarget.attributes;
            const street = attributes["data-street"];
            this.real_address_recovery.val(street.value);
            this._check_input_recuperation();
        },
        _onClickRecuperationButton: async function (events) {
            await this._super.apply(this, arguments)
            if (!this.address_recuperation.val()) {
                this.div_recuperation.siblings("small").remove();
                this.div_recuperation.after(this.errosHtmlMessage);
                this.address_recuperation.css("border-color", "red");
            } else {
                await rpc.query({
                    route: "/evtc/save_address",
                    params: {
                        street: this.address_recuperation.val(),
                        latitude: $("#latitude_address_recovery").val(),
                        longitude: $("#longitude_address_recovery").val(),
                        is_historical: true,
                    },
                });
                this.recuperation_adress_heading.contents().eq(4).remove();
                this.recuperation_adress.after(this.address_recuperation.val());
                this.div_recuperation.siblings("small").remove();
                this.address_recuperation.css("border-color", "black");
                $("#evtc_aside").animate({ scrollTop: $("#where_do_you_go").position().top });
                let values = this.address_recuperation.val();
                const lat = $("#latitude_address_recovery").val();
                const lng = $("#longitude_address_recovery").val();
                this._computeAutoClass(events, 'evtc_recuperation', 'evtc_recuperation_button', values, lat, lng)
            }
        },
    });
});
