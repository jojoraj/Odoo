odoo.define('evtc_pos.SaleOrderButtonClickQuotation', function (require) {
    "use strict";

    const SaleOrderButtonClickQuotation = require("pos_sale.SetSaleOrderButton")
    const Registries = require('point_of_sale.Registries');
    const VtcAreaDestination = require('vtc_area_destination.OeTimeWaitCoursePause')

    const ExtendsSaleOrderButton = SaleOrderButtonClickQuotation => class extends SaleOrderButtonClickQuotation {
        async onClick() {
            const isProccessOnclick = await this.checkOrderVtc()
            if (isProccessOnclick) {
                await super.onClick()
            }
        }

        async checkOrderVtc() {
            let order = this.env.pos.get_order()
            if (order.orderlines.models.length > 0) {
                return this.showPopupVtcNotification(order)
            }
            return true;
        }

        async showPopupVtcNotification(orders) {
            const { confirmed } = await this.showPopup('ConfirmPopup', {
                'title': this.env._t('Commad'),
                'body': this.env._t('Please complete or delete the current order before choosing another\n' +
                    'Do you want to delete current orderline?'
                ),
                confirmText: this.env._t('Continue'),
                cancelText: this.env._t('Delete'),
            });
            if (confirmed) {
                return false
            }
            orders.orderlines.models.forEach(lines => {
                lines.set_quantity('remove')
            });
            return true
        }
    };
    Registries.Component.extend(SaleOrderButtonClickQuotation, ExtendsSaleOrderButton)
    return ExtendsSaleOrderButton;
});
