odoo.define("vtc_area_destination.evtc_template_inherit", function(require) {
    "use strict";

    const vehicle = require("evtc_front.reservations");
    vehicle.evtcArkeupMap.include({
        start: async function() {
            await this._super.apply(this, arguments);
        },

        _on_click_vehicle_button: async function() {
            await this._super.apply(this, arguments);
            const myCustomHtml =
                `
                <span>
                    <span>à :</span>
                        <i class="picto picto-address-black mr-2" id="destination_adress"/>
                        ` +
                this.lastDestination +
                `
                </span>
            `;
            this.$("#destination_adress_heading_vehicle").empty();
            this.$("#destination_adress_heading_vehicle").append(myCustomHtml);
        },
    });
});
