odoo.define("evtc_taxi.vehicle_template", function(require) {
    "use strict";

    const VehicleTemplate = require("evtc_front.reservations");
    VehicleTemplate.evtcArkeupMap.include({
        _onClickVehicleButton: async function() {
            await this._super.apply(this, arguments);
            sessionStorage.setItem(
                "taxi",
                $("input[name='vehicle_customRadio']:checked").data()["taxi"] === "True"
            );
        },
    });
});
