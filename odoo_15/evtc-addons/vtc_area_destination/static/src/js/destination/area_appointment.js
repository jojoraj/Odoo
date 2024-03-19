odoo.define("vtc_area_destination.evtc_appointment_inherit", function (require) {
    "use strict";

    const vtc_appointment = require("evtc_front.reservations");
    vtc_appointment.evtcArkeupMap.include({
        start: async function () {
            await this._super.apply(this, arguments);
        },

        _on_click_appoitment_button: async function () {
            await this._super.apply(this, arguments);
            const myCustomHtml =
                `
                <span>
                    <span>à :</span> <i class="picto picto-address-black mr-2" id="destination_adress"/>
                        ` + this.lastDestination + ` </span>
            `;
            this.$("#destination_adress_heading_appointment").empty();
            this.$("#destination_adress_heading_appointment").append(myCustomHtml);
        },
    });
});
