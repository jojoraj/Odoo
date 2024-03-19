odoo.define("vtc_area_destination.evtc_payment_inherit", function(require) {
    "use strict";

    const vtc_payment = require("evtc_front.reservations");
    vtc_payment.evtcArkeupMap.include({

        start: async function() {
            await this._super.apply(this, arguments);
        },
        _on_click_payment_button: async function() {
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
            this.$("#destination_adress_heading_payment").empty();
            this.$("#destination_adress_heading_payment").append(myCustomHtml);
            this.$("#heading_payment_resume_modal_media_body").empty();
            this.$("#heading_payment_resume_modal_media_body").append(
                `<p class="d-none place_val"/>` + this.lastDestination
            );
        },
    });
});
