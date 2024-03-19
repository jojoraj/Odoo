odoo.define('etech_auto_planning.SaleOrderRow', function (require) {
    'use strict';

    const SaleOrderRow = require('pos_sale.SaleOrderRow');
    const Registries = require('point_of_sale.Registries');
    var tabId = [];
    const ExtendsSaleOrderRow = SaleOrderRow =>
        class extends SaleOrderRow {
            get date() {
                if (this.order.pick_up_datetime) {
                    if (!tabId.includes(this.order.id))
                    {
                        tabId.push(this.order.id);
                        var date = new Date(this.order.pick_up_datetime);
                        var userTimezoneOffset = date.getTimezoneOffset() / 60;
                        date.setHours((date.getHours() - userTimezoneOffset));
                        this.order.pick_up_datetime = moment(date).format('YYYY-MM-DD HH:mm:ss');
                    }

                    return this.order.pick_up_datetime;
                }
                    return moment(this.order.date_order).format('YYYY-MM-DD hh:mm A');

                ;
            }

        };

    Registries.Component.extend(SaleOrderRow, ExtendsSaleOrderRow);
    return ExtendsSaleOrderRow;
})
;
