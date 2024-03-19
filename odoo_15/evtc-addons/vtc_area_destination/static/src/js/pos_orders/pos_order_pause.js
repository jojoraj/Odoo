odoo.define('vtc_area_destination.OeTimeWaitCoursePause', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc');

    let clickRecords = 0
    let totalSecond = 0
    let totalMins = 0
    let totalHours = 0
    let order_id = undefined
    let isRecords = true
    let timePassed = true

    const nameStatusPause = 'Temps de pause'
    const nameStatusPlay = 'Reprendre la course'
    const statusPauseIcon = 'fa-pause'
    const statusPlayIcon = 'fa-play'

    function _getHMS(val) {
        return (String(val)).length < 2 ? "0" + val : String(val)
    }

    class OeTimeWaitCoursePause extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.setCoursePause);
        }

        async setCoursePause(events) {
            events.preventDefault()
            this.setIntervallTimer();
            const StopBtn = $('#stop-btn');
            const nameStatus = $('#name-status')
            const iconStatus = $('#icon-font-status')
            const removeTimers = $('#onRemoveTimers')
            nameStatus[0].innerHTML = clickRecords % 2 === 0 ? nameStatusPlay : nameStatusPause
            if (clickRecords % 2 === 0) {
                StopBtn.css("background-color", "#9593939e");
                StopBtn.addClass("disabled");
                removeTimers[0].style.display = 'block';
                if (iconStatus.hasClass(statusPlayIcon)) {
                    iconStatus.removeClass(statusPlayIcon)
                    iconStatus.addClass(statusPauseIcon)
                }
            } else {
                StopBtn.css("background-color", "#ff00004f");
                StopBtn.removeClass("disabled");
                if (iconStatus.hasClass(statusPauseIcon)) {
                    iconStatus.addClass(statusPlayIcon)
                    iconStatus.removeClass(statusPauseIcon)
                }
            }
            isRecords = clickRecords % 2 === 0
            this.update_price_quantity()
            ++clickRecords;
        }

        async start() {
            this._super.apply(...arguments);
        }

        _show_after(delay) {
            return new Promise(function (resolve) {
                setTimeout(resolve, delay);
            });
        }

        check_order(new_order) {
            if (order_id == undefined) {
                order_id = new_order
            } else if (new_order != order_id) {
                order_id = new_order
                this._init_timers()
            }
        }

        async setIntervallTimer() {
            let current_order_id = this.get_order_by_orderline()
            if (current_order_id){
                this.check_order(current_order_id)
            }
            if (timePassed) {
                setInterval(this._setTimers, 1000);
                timePassed = false
            }
        }

        _init_timers() {
            totalHours = 0;
            totalMins = 0;
            totalSecond = 0;
        }

        _setTimers() {
            const minutesLabel = $("#minutes")[0];
            const secondsLabel = $("#seconds")[0];
            const hoursLabel = $("#hours")[0];
            if (isRecords && minutesLabel && secondsLabel && hoursLabel) {
                ++totalSecond;
                secondsLabel.innerHTML = _getHMS(totalSecond % 60);
                totalMins = parseInt(totalSecond / 60)
                if (totalMins > 59) {
                    ++totalHours;
                    totalMins = 0
                }
                minutesLabel.innerHTML = _getHMS(totalMins);
                hoursLabel.innerHTML = _getHMS(totalHours);
            }
        }

        get_order_by_orderline(){
            const order_origin = this.env.pos.get_order().orderlines.models.filter(v => v.sale_order_origin_id)
            return order_origin ? order_origin[0].sale_order_origin_id.id : undefined
        }

        async update_price_quantity() {
            const minutesLabel = $("#minutes")[0];
            const secondsLabel = $("#seconds")[0];
            const hoursLabel = $("#hours")[0];
            while (isRecords && minutesLabel && secondsLabel && hoursLabel) {
                await this._show_after(10000).then(async (x) => {
                    try {
                        const quant = totalMins + totalHours * 60
                        const args = []
                        await rpc.query({
                            model: 'area.time.wait',
                            method: 'get_price_unit',
                            args: [args],
                            kwargs: { 'min': quant }
                        }).then(price => {
                            const lines = this.env.pos.get_order().orderlines;
                            let current_order = this.get_order_by_orderline()
                            lines.models.forEach(async line => {
                                if (line.product.time_wait_ok) {
                                    if (current_order != undefined) {
                                        const values = {
                                            order_id: current_order,
                                            quantity: quant,
                                            price: price
                                        }
                                        await rpc.query({
                                            model: 'sale.order',
                                            method: 'set_real_time_wait',
                                            args: [args],
                                            kwargs: values
                                        }).then(x => {
                                            line.set_lst_price(price)
                                            line.set_unit_price(price)
                                            line.set_quantity(1)
                                            totalMins = parseInt(totalSecond / 60)
                                            line.hasNote = "Temps d'attente  " + _getHMS(totalHours) + ':' + _getHMS(totalMins)
                                        })
                                    }
                                }
                            })
                        })
                    } catch (e) {
                        isRecords = false
                    }
                })
            }
        }
    }

    OeTimeWaitCoursePause.template = 'OeTimeWaitCoursePause';

    ProductScreen.addControlButton({
        component: OeTimeWaitCoursePause,
        condition: function () {
            return true;
        },
        position: ['after', 'GeotabPosOrder'],
    });

    Registries.Component.add(OeTimeWaitCoursePause);

    return OeTimeWaitCoursePause;

});
