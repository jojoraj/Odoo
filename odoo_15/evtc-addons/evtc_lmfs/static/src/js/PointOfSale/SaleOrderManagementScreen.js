odoo.define('evtc_lmfs.SaleOrderManagementScreen', function (require) {
    'use strict';

    const Cookie = require('web.utils.cookies');
    const SaleOrderManagementScreen = require('pos_sale.SaleOrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');

    const SaleOrdersManagement = SaleOrderManagementScreen => class extends SaleOrderManagementScreen {

        async _get_popup_render_options() {
            const {confirmed, payload: SelectedOption} = await this.showPopup('SelectionPopup',
                {
                    title: this.env._t('What do you want to do?'),
                    list: [{id: "0", label: this.env._t("Apply a down payment"), item: false}, {
                        id: "1",
                        label: this.env._t("Settle the order"),
                        item: true
                    }],
                });
            return {confirm: confirmed, options: SelectedOption}
        }

        async _orderLinesRequest(line, clickedOrder) {
            return {
                pos: this.env.pos,
                order: this.env.pos.get_order(),
                product: this.env.pos.db.get_product_by_id(line.product_id[0]),
                price: line.price_unit,
                price_manually_set: true,
                sale_order_origin_id: clickedOrder,
                sale_order_line_id: line,
                customer_note: line.customer_note,
            }
        }

        async _orderLinesDownPayment(down_payment, clickedOrder, tab) {
            return {
                pos: this.env.pos,
                order: this.env.pos.get_order(),
                product: this.env.pos.db.get_product_by_id(this.env.pos.config.down_payment_product_id[0]),
                price: down_payment,
                price_manually_set: true,
                sale_order_origin_id: clickedOrder,
                down_payment_details: tab,
            }
        }

        async _sync_order_price_list(PricePOSOrder, sale_order) {
            const orderPricelist = sale_order.pricelist_id ? this.env.pos.pricelists.find(
                (pricelist) => pricelist.id === sale_order.pricelist_id[0]) : false;
            if (orderPricelist) {
                PricePOSOrder.set_pricelist(orderPricelist);
            }
        }

        async _sync_order_fiscal_pos(FiscalPOSOrder, sale_order) {
            const orderFiscalPos = sale_order.fiscal_position_id ? this.env.pos.fiscal_positions.find(
                (position) => position.id === sale_order.fiscal_position_id[0]) : false;
            if (orderFiscalPos) {
                FiscalPOSOrder.fiscal_position = orderFiscalPos;
            }
        }

        async _sync_order_data(POSOrderData, clickedOrder, sale_order) {
            try {
                await this.env.pos.load_new_partners();
            } catch (error) {
                /*
                * do nothing
                * */
            }
            POSOrderData.set_client(
                this.env.pos.db.get_partner_by_id(sale_order.partner_id[0])
            );
            await this._sync_order_fiscal_pos(POSOrderData, sale_order)
            await this._sync_order_price_list(POSOrderData, sale_order)
        }

        async _confirm_import_product_pos_missing(lines) {
            const product_to_add_in_pos = lines.filter(line => !this.env.pos.db.get_product_by_id(line.product_id[0])).map(line => line.product_id[0]);
            if (product_to_add_in_pos.length) {
                const {confirmed} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Products not available in POS'),
                    body:
                        this.env._t(
                            'Some of the products in your Sale Order are not available in POS, do you want to import them?'
                        ),
                    confirmText: this.env._t('Yes'),
                    cancelText: this.env._t('No'),
                });
                if (confirmed) {
                    await this.env.pos._addProducts(product_to_add_in_pos);
                }
            }
        }

        async _sync_load_order_sn_lots(new_line, line) {
            let useLoadedLots;
            if (
                new_line.get_product().tracking !== 'none' &&
                (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots) &&
                line.lot_names.length > 0
            ) {
                // Ask once when `useLoadedLots` is undefined, then reuse it's value on the succeeding lines.
                const {confirmed} = useLoadedLots === undefined ? await this.showPopup('ConfirmPopup', {
                    title: this.env._t('SN/Lots Loading'),
                    body: this.env._t(
                        'Do you want to load the SN/Lots linked to the Sales Order?'
                    ),
                    confirmText: this.env._t('Yes'),
                    cancelText: this.env._t('No'),
                }) : {confirmed: useLoadedLots};
                useLoadedLots = confirmed;
                if (useLoadedLots) {
                    new_line.setPackLotLines({
                        modifiedPackLotLines: [],
                        newPackLotLines: (line.lot_names || []).map((name) => ({lot_name: name})),
                    });
                }
            }
            await this._sync_order_values(new_line, line)
        }

        async _order_real_trip_values(currentOrderLine, assertLine) {
            const role_id = this.env.pos.config.role_id[0]
            const orderLineID = assertLine.id
            await this.rpc({
                model: 'sale.order.line',
                method: 'get_orderline_values',
                args: [[orderLineID], role_id],
            }).then(trip => {
                if (trip.status) {
                    currentOrderLine.set_quantity(trip.result.quant)
                    if (!trip.result.is_km_unit) {
                        currentOrderLine.set_unit_price(trip.result.priceUnit)
                        if (trip.result.lineNote) {
                            currentOrderLine.hasNote = trip.result.lineNote
                        }
                    }
                }
            })
        }

        async _sync_order_values(new_line, line) {
            new_line.setQuantityFromSOL(line);
            new_line.set_unit_price(line.price_unit);
            new_line.set_discount(line.discount);
            await this._order_real_trip_values(new_line, line)
            this.env.pos.get_order().add_orderline(new_line);
            Cookie.set_cookie('start_enabled', true)
        }

        async _apply_down_payment_request(sale_order, clickedOrder) {
            const lines = sale_order.order_line;
            const tab = [];

            for (let i = 0; i < lines.length; i++) {
                tab[i] = {
                    'product_name': lines[i].product_id[1],
                    'product_uom_qty': lines[i].product_uom_qty,
                    'price_unit': lines[i].price_unit,
                    'total': lines[i].price_total,
                };
            }
            let down_payment = sale_order.amount_total;
            const {confirmed, payload} = await this.showPopup('NumberPopup', {
                title: _.str.sprintf(this.env._t("Percentage of %s"), this.env.pos.format_currency(sale_order.amount_total)),
                startingValue: 0,
            });
            if (confirmed) {
                down_payment = sale_order.amount_total * parseFloat(payload) / 100;
            }
            if (this.env.pos.config.down_payment_product_id[0]) {
                let order_lines_values = await this._orderLinesDownPayment(down_payment, clickedOrder, tab)
                const new_line = new models.Orderline({}, order_lines_values);
                new_line.set_unit_price(down_payment);
                this.env.pos.get_order().add_orderline(new_line);
            }
        }

        async _apply_set_payment(sale_order, clickedOrder) {
            const lines = sale_order.order_line;
            await this._confirm_import_product_pos_missing(lines)
            for (var i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (!this.env.pos.db.get_product_by_id(line.product_id[0])) {
                    continue;
                }
                let orderline_values = await this._orderLinesRequest(line, clickedOrder)
                const new_line = new models.Orderline({}, orderline_values);
                await this._sync_load_order_sn_lots(new_line, line)
            }
        }

        async _onClickSaleOrder(event) {
            const clickedOrder = event.detail;
            const PopupRender = await this._get_popup_render_options(clickedOrder)
            const confirmed = PopupRender.confirm
            const selectedOption = PopupRender.options
            if (confirmed) {
                const currentPOSOrder = this.env.pos.get_order();
                const sale_order = await this._getSaleOrder(clickedOrder.id)
                await this._sync_order_data(currentPOSOrder, clickedOrder, sale_order)
                if (selectedOption) {
                    await this._apply_set_payment(sale_order, clickedOrder)
                } else {
                    await this._apply_down_payment_request(sale_order, clickedOrder)
                }
                currentPOSOrder.trigger('change');
                this.close();
            }

        }
    };
    Registries.Component.extend(SaleOrderManagementScreen, SaleOrdersManagement)
    return SaleOrdersManagement;
});
