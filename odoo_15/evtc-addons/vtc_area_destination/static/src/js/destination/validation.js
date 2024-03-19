odoo.define("vtc_area_destination.area_validation", function(require) {
    "use strict";

    const rpc = require("web.rpc");
    const EvtcMaps = require("evtc_front.reservations");
    EvtcMaps.evtcArkeupMap.include({
        start: async function() {
            await this._super.apply(this, arguments);
        },
        _check_input_destination: function() {
            /*
             * Override method to do nothings
             * check on input value
             * */
        },

        _remove_all_errors_message: function() {
            const fieldInput = this.$("#address_destination");
            this.$(".oe_errors_message").remove();
            if (fieldInput.length > 0) {
                fieldInput.css("border-color", "black");
            }
        },

        _show_erros: function() {
            this._remove_all_errors_message();
            const fieldInput = this.$("#address_destination");
            if (fieldInput.length > 0) {
                fieldInput.css("border-color", "red");
                fieldInput.after(
                    '<small class="text-danger oe_errors_message">Veuillez remplir le champ où sélectionné parmi les adresses enregistrer</small>'
                );
            }
        },

        resolvePromiseWait: function(delay) {
            return new Promise(function(resolve) {
                setTimeout(resolve, delay);
            });
        },

        _performOnclickDestination: async function(events) {
            let renderValues = {
                process: true,
                errors: undefined,
            };

            let is_passed = false;

            const InputDestination = this.$("#address_destination")[0];
            const latDestination = this.$("#latitude_address_destination")[0];
            const lngDestination = this.$("#longitude_address_destination")[0];
            if (
                this.txContext.is_first &&
                InputDestination &&
                InputDestination.value &&
                latDestination &&
                latDestination.value &&
                lngDestination &&
                lngDestination.value
            ) {
                is_passed = true;
            }
            if (this.txContext && this.txContext.destination.length >= 1) {
                is_passed = true;
            }
            const hasOnErrors = $(".direction_server");
            if (hasOnErrors.length > 0) {
                hasOnErrors.remove();
            }
            if (this.direction_service_error.state) {
                is_passed = false;
                const message = `
                        <div class="alert alert-warning position-relative w-100 direction_server">
                        Veuillez vérifier votre dernière destination car aucune route n'a été trouver en y passant
                        </div>
                    `;
                $("#evtc_destination_button").before(message);
            }

            if (this.txContext && this.txContext.destination.length === 1) {
                $(this.$(".save-recently-wrap")).attr("style", "display: none !important;");
                is_passed = true;
            }

            if (is_passed) {
                const value =
                    `
                        <span>
                            <span>à :</span>
                                <i class="picto picto-address-black mr-2" id="destination_adress"></i>
                                ` +
                    this.lastDestination +
                    `
                        </span>
                    `;
                this.$("#destination_adress_heading").empty();
                this.$("#destination_adress_heading").append(value);
                this.txContext.destination.forEach((data) => {
                    rpc.query({
                        route: "/evtc/save_address",
                        params: {
                            street: data.name,
                            latitude: data.position.lat,
                            longitude: data.position.lng,
                            is_historical: true,
                        },
                    });
                });
                if (this.txContext && this.txContext.destination.length > 1) {
                    $(this.el).find("#length_target")[0].innerText = this.AllDistance;
                    $(this.el).find("#waiting")[0].innerText = window.allTimeWait;
                } else if (this.txContext && this.txContext.destination.length === 1) {
                    $(this.el).find("#waiting")[0].innerText =
                        this.txContext.destination[0].details.name;
                    $(this.el).find("#length_target")[0].innerText = this.lengthDistanceStrip;
                    $(this.el).find("#duration")[0].innerText = this.DurationStrip;
                }

                this.recuperation_adress_heading_destination.contents().eq(4).remove();
                this.recuperation_adress_destination.after(this.address_recuperation.val());
                this.destination_adress_heading.contents().eq(4).remove();
                this.destination_adress.after(this.address_destination.val());
                this.div_destination.siblings("small").remove();
                this.address_destination.css("border-color", "black");
                this.destination.addClass("d-none");
                this.appointment.removeClass("d-none");
                $("#evtc_aside").animate({ scrollTop: $("#evtc_aside").height() });
                $("#evtc_aside").animate({ scrollTop: $("#when").position().top });
                this._remove_all_errors_message();
                let values = this.txContext.destination.length > 1 ? this.mappedDestinationName() : this.txContext.destination[0].name
                this._computeAutoClass(events, 'evtc_destination', 'evtc_destination_button', values, '', '')
            } else {
                this._show_erros();
            }
            return renderValues;
        },

        mappedDestinationName: function() {
            let name = '';
            this.txContext.destination.forEach(e => {
                if (e.name) {
                    name += e.name + ', '
                }
            })
            return name
        }
    });
});
