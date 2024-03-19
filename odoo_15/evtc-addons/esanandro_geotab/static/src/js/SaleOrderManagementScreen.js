odoo.define('esanandro_geotab.SaleOrderManagementScreen', function (require) {
    'use strict';

    const Cookie = require('web.utils.cookies');
    const SaleOrderManagementScreen = require('pos_sale.SaleOrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');
    var field_utils = require('web.field_utils');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;

    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity, keep_price) {
            this.order.assert_editable();
            if (quantity === 'remove') {
                if (this.refunded_orderline_id in this.pos.toRefundLines) {
                    delete this.pos.toRefundLines[this.refunded_orderline_id];
                }
                this.order.remove_orderline(this);
                var orderline_length = this.order.orderlines.length

                if (orderline_length === 0) {
                    Cookie.set_cookie('start_enabled', false)
                    $("#start-btn").css("background-color", "#9593939e");
                    $("#start-btn").addClass("disabled");
                    $("#localiz_btn").css("background-color", "#9593939e");
                    $("#localiz_btn").addClass("disabled");
                    return true;
                }
                return true


            }
                var quant = typeof (quantity) === 'number' ? quantity : (field_utils.parse.float(String(quantity)) || 0);
                if (this.refunded_orderline_id in this.pos.toRefundLines) {
                    const toRefundDetail = this.pos.toRefundLines[this.refunded_orderline_id];
                    const maxQtyToRefund = toRefundDetail.orderline.qty - toRefundDetail.orderline.refundedQty
                    if (quant > 0) {
                        Gui.showPopup('ErrorPopup', {
                            title: _t('Positive quantity not allowed'),
                            body: _t('Only a negative quantity is allowed for this refund line. Click on +/- to modify the quantity to be refunded.')
                        });
                        return false;
                    } else if (quant === 0) {
                        toRefundDetail.qty = 0;
                    } else if (-quant <= maxQtyToRefund) {
                        toRefundDetail.qty = -quant;
                    } else {
                        Gui.showPopup('ErrorPopup', {
                            title: _t('Greater than allowed'),
                            body: _.str.sprintf(
                                _t('The requested quantity to be refunded is higher than the refundable quantity of %s.'),
                                this.pos.formatProductQty(maxQtyToRefund)
                            ),
                        });
                        return false;
                    }
                }
                var unit = this.get_unit();
                if (unit) {
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        this.quantity = round_pr(quant, rounding);
                        this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                    } else {
                        this.quantity = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                } else {
                    this.quantity = quant;
                    this.quantityStr = String(this.quantity);
                }


            // Just like in sale.order changing the quantity will recompute the unit price
            if (!keep_price && !this.price_manually_set) {
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
                this.order.fix_tax_included_price(this);
            }
            this.trigger('change', this);
            return true;
        },
    })


    const ExtendsSaleOrderManagementScreen = SaleOrderManagementScreen =>
        class extends SaleOrderManagementScreen {
            async _onClickSaleOrder(event) {

                const clickedOrder = event.detail;
                const {confirmed, payload: selectedOption} = await this.showPopup('SelectionPopup',
                    {
                        title: this.env._t('What do you want to do?'),
                        list: [{id: "0", label: this.env._t("Apply a down payment"), item: false}, {
                            id: "1",
                            label: this.env._t("Settle the order"),
                            item: true
                        }],
                    });

                if (confirmed) {
                    const currentPOSOrder = this.env.pos.get_order();
                    const sale_order = await this._getSaleOrder(clickedOrder.id);
                    try {
                        await this.env.pos.load_new_partners();
                    } catch (error) {
                    }
                    currentPOSOrder.set_client(this.env.pos.db.get_partner_by_id(sale_order.partner_id[0]));
                    const orderFiscalPos = sale_order.fiscal_position_id ? this.env.pos.fiscal_positions.find(
                            (position) => position.id === sale_order.fiscal_position_id[0]
                        )
                        : false;
                    if (orderFiscalPos) {
                        currentPOSOrder.fiscal_position = orderFiscalPos;
                    }
                    const orderPricelist = sale_order.pricelist_id ? this.env.pos.pricelists.find(
                            (pricelist) => pricelist.id === sale_order.pricelist_id[0]
                        )
                        : false;
                    if (orderPricelist) {
                        currentPOSOrder.set_pricelist(orderPricelist);
                    }

                    if (selectedOption) {
                        // Settle the order
                        const lines = sale_order.order_line;
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

                        /**
                         * This letiable will have 3 values, `undefined | false | true`.
                         * Initially, it is `undefined`. When looping thru each sale.order.line,
                         * when a line comes with lots (`.lot_names`), we use these lot names
                         * as the pack lot of the generated pos.order.line. We ask the user
                         * if he wants to use the lots that come with the sale.order.lines to
                         * be used on the corresponding pos.order.line only once. So, once the
                         * `useLoadedLots` becomes true, it will be true for the succeeding lines,
                         * and vice versa.
                         */
                        let useLoadedLots;

                        for (var i = 0; i < lines.length; i++) {
                            const line = lines[i];
                            if (!this.env.pos.db.get_product_by_id(line.product_id[0])) {
                                continue;
                            }

                            const new_line = new models.Orderline({}, {
                                pos: this.env.pos,
                                order: this.env.pos.get_order(),
                                product: this.env.pos.db.get_product_by_id(line.product_id[0]),
                                price: line.price_unit,
                                price_manually_set: true,
                                sale_order_origin_id: clickedOrder,
                                sale_order_line_id: line,
                                customer_note: line.customer_note,
                            });

                            if (
                                new_line.get_product().tracking !== 'none' &&
                                (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots) &&
                                line.lot_names.length > 0
                            ) {
                                // Ask once when `useLoadedLots` is undefined, then reuse it's value on the succeeding lines.
                                const {confirmed} =
                                    useLoadedLots === undefined
                                        ? await this.showPopup('ConfirmPopup', {
                                            title: this.env._t('SN/Lots Loading'),
                                            body: this.env._t(
                                                'Do you want to load the SN/Lots linked to the Sales Order?'
                                            ),
                                            confirmText: this.env._t('Yes'),
                                            cancelText: this.env._t('No'),
                                        })
                                        : {confirmed: useLoadedLots};
                                useLoadedLots = confirmed;
                                if (useLoadedLots) {
                                    new_line.setPackLotLines({
                                        modifiedPackLotLines: [],
                                        newPackLotLines: (line.lot_names || []).map((name) => ({lot_name: name})),
                                    });
                                }
                            }
                            new_line.setQuantityFromSOL(line);
                            new_line.set_unit_price(line.price_unit);
                            new_line.set_discount(line.discount);
                            this.env.pos.get_order().add_orderline(new_line);
                            Cookie.set_cookie('start_enabled', true)
                        }
                    } else {
                        // Apply a downpayment
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
                            const new_line = new models.Orderline({}, {
                                pos: this.env.pos,
                                order: this.env.pos.get_order(),
                                product: this.env.pos.db.get_product_by_id(this.env.pos.config.down_payment_product_id[0]),
                                price: down_payment,
                                price_manually_set: true,
                                sale_order_origin_id: clickedOrder,
                                down_payment_details: tab,
                            });
                            new_line.set_unit_price(down_payment);
                            this.env.pos.get_order().add_orderline(new_line);
                        }

                    }

                    currentPOSOrder.trigger('change');
                    this.close();
                }

            }
        };
    Registries.Component.extend(SaleOrderManagementScreen, ExtendsSaleOrderManagementScreen)
    return ExtendsSaleOrderManagementScreen;
});
