odoo.define("vtc_area_destination.evtc_template_resume_inherit", function(require) {
    "use strict";

    const vehicleResumeWidget = require("evtc_front.reservations");
    vehicleResumeWidget.evtcArkeupMap.include({
        start: async function() {
            await this._super.apply(this, arguments);
        },

        _on_click_vehicle_resume_button: async function() {
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
            this.$("#destination_adress_heading_vehicle_resume").empty();
            this.$("#destination_adress_heading_vehicle_resume").append(myCustomHtml);
        },
    });
});
