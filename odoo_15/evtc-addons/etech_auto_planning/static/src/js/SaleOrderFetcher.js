odoo.define('etech_auto_planning.SetSaleOrderButton', function (require) {
    'use strict';
    const components = {SaleOrderFetcher: require("pos_sale.SaleOrderFetcher")};
    const {patch} = require("web.utils");
    let jsFile = "etech_auto_planning/static/src/js/SaleOrderFetcher.js"
    patch(
        components.SaleOrderFetcher, jsFile, {
            async _getOrdersPos(limit, offset, values) {
                const role_id = this.comp.env.pos.config.role_id[0];
                let roleOrders = await this.rpc({
                    model: "planning.slot",
                    method: 'get_order_ids',
                    args: [role_id, this.searchDomain, limit + 1, offset],
                    context: this.comp.env.session.user_context,
                });
                return values === 'count' ? roleOrders.ordersCount : roleOrders.orders
            },
            async _getOrderIdsForCurrentPage(limit, offset) {
                return this._getOrdersPos(limit, offset, 'orders')
            },

            async _fetch(limit, offset) {
                let sale_orders = await this._super(limit, offset);
                this.totalCount = await this._getOrdersPos(limit, offset, 'count')
                return sale_orders;
            }
        }
    )
})
