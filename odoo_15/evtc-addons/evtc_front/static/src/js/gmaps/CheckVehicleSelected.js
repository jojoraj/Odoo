odoo.define('lcas.evtc.CheckVehicleSelected', function (require) {
    'use strict';
    var JsRpc = require('web.ajax');
    const CheckVehicleSelected = require('evtc_front.reservations');
    const SelectedVechicle = CheckVehicleSelected.evtcArkeupMap;

    const selected = SelectedVechicle.include({
        events: _.extend({}, SelectedVechicle.prototype.events, {
            'click #evtc_vehicle_button': '_onClickVehicleButton',
        }),
        __selectors: function () {
            this._super.apply(this, arguments);
            this.records = $("input[name='vehicle_customRadio']:checked")[0]
        },

        _bindClickVehicle: async function () {
            this.updateRatesAndMinimum();
            await this.calculateAndDisplayTotal();
            this.updateCurrencyConversions();
        },

        _onClickVehicleButton: async function (events) {
            events.preventDefault()
            await this._bindClickVehicle()
        },

        _estimatedTravelDistance: async function (estimatedTravel) {
            const kilometers = $('#length_target').text() || 0;
            return parseFloat(kilometers) <= parseFloat(estimatedTravel) ? parseFloat(estimatedTravel) : parseFloat(kilometers)
        },

        _formatNumber: function (n) {
            return new Intl.NumberFormat().format(n);
        },

        _updateText: function (selector, text) {
            $(this.el).find(selector)[0].innerText = text
        },

        _updateMinimumTotal: function (value) {
            $('#total_min_to_pay').text(`${this._formatNumber(value)} Ar`);
        },

        updateRatesAndMinimum: function () {
            const self = this;
            const vehicleRadio = $("input[name='vehicle_customRadio']:checked")[0];
            const rate = parseFloat(vehicleRadio.dataset.rate);
            const minimumRate = parseFloat(vehicleRadio.dataset.minimumRate) || 0;
            this.vehicle_rate_per_km = rate;

            self._updateText('#vehicle_rate', self._formatNumber(rate));
            self._updateText('#minimum_price', self._formatNumber(minimumRate));
            self._updateMinimumTotal(minimumRate)
        },

        _removeTextRate: function (checked) {
            if (checked) {
                $('#or_min_message').addClass('d-none');
            } else {
                $('#or_min_message').removeClass('d-none');
            }
        },

        calculateAndDisplayTotal: async function () {
            const self = this;
            const d = await self._estimatedTravelDistance(self.kilometers_estimation)
            await self._removeDisplayNone()
            const total = Math.ceil(d * self.vehicle_rate_per_km / 1000) * 1000;
            const minimumRate = parseFloat($("input[name='vehicle_customRadio']:checked")[0].dataset.minimumRate) || 0;
            self._removeTextRate(minimumRate === 0)
            const displayMinMessage = minimumRate > 0 && total < minimumRate;
            await self._checkDisplayTotalCount(displayMinMessage);
            const finalAmount = displayMinMessage ? minimumRate : total;
            $("#total_to_pay").text(`${self._formatNumber(finalAmount)} Ar`);
        },


        _removeDisplayNone: function () {
            $('#total_min_to_pay').removeClass('d-none');
            $('#total_to_pay').removeClass('d-none');
            this._removeAttrStyle()
        },

        _toggleMinimumDiv: function (h) {
            $('#total_min_to_pay').toggleClass('d-none', h)
        },

        _toggleTotalDiv: function (f) {
            $('#total_to_pay').toggleClass('d-none', f)
        },

        _removeAttrStyle: function () {
            $('#total_min_to_pay').attr("style", "")
            $('#total_to_pay').attr("style", "")
        },

        _checkDisplayTotalCount: async function (IsMinimum) {
            this._toggleMinimumDiv(!IsMinimum)
            this._toggleTotalDiv(IsMinimum)
        },

        updateCurrencyConversions: function () {
            const kilometers = parseFloat(this.kilometers_estimation);
            const total = Math.ceil(kilometers * this.vehicle_rate_per_km / 1000) * 1000;
            JsRpc.jsonRpc('/web/get/usd-euro/currency-id', 'call', {})
                .then((result) => {
                    $('#usd_price').text((total * result.usd).toFixed(2));
                    $('#euro_price').text((total * result.eur).toFixed(2));
                });
        },

    });
    return selected
})
