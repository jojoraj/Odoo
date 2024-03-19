odoo.define("evtc_pos.removeOrderLine", function (require) {
    "use strict";

    const Orderline = require("point_of_sale.Orderline");
    const Registries = require("point_of_sale.Registries");

    const PosOrderline = (Orderline) =>
        class extends Orderline {
            removeLines() {
                this.props.line.set_quantity("remove");
            }
        };
    Registries.Component.extend(Orderline, PosOrderline);
    return Orderline;
});
