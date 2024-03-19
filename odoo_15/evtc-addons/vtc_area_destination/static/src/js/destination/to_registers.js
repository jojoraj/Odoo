odoo.define('vtc_area_destination.to_registers', function(require) {
    'use strict';

    const vtcMap = require('evtc_front.reservations')

    vtcMap.evtcArkeupMap.include({

        events: _.extend({}, vtcMap.evtcArkeupMap.prototype.events, {
            'click .to-register': '_onClickRegister',
        }),

        start: async function() {
            await this._super.apply(this, arguments)
        },

        _add_real_time_details: function(treal, details) {
            if (details) {
                details.real_time = treal
            } else {
                details = { real_time: treal }
            }
            return details
        },

        _onClickRegister: async function() {
            const self = this;
            const hasObject = {
                modification_id: 0,
                lat: null,
                lng: null,
                status: 'new',
                hasRegister: this._init_destination(true),
                isUpdate: false,
            }
            this._update_selector_value()
            if (this.check_validate_coordinate()) {

                const latlng = this.$('#autocomplete-x1dCV')
                if (latlng[0] && latlng[0].classList.contains('next-content-suggestion')) {
                    hasObject.lat = latlng.next()[0].value
                    hasObject.lng = latlng.next().next()[0].value
                }
                const parameter = await this._get_params(hasObject)

                this._toggle_add_destination()

                try {
                    const real_time = Boolean(parameter._CurrentObject.details)
                    const transientDetails = self._add_real_time_details(real_time, parameter._CurrentObject.details)
                    parameter._CurrentObject.details = transientDetails
                    if (parameter.Price) {
                        parameter.Price.real_time = transientDetails
                    }

                    this._createLiOption(parameter)
                    const destination = this.txContext.destination.filter(res => res.id === this.transientMarker.slice(-1)[0].marker_id)[0]
                    if (destination && destination.id === this.transientMarker.slice(-1)[0].marker_id) {
                        destination.marker = this.transientMarker.slice(-1)[0]
                        this.transientMarker = []
                    }

                    this._remove_all_errors_message()

                    await this._reorderSequence()

                } catch (e) {
                    if (self.try_laters < 2) {
                        self.try_laters += 1;
                        self._onClickRegister()
                    } else {
                        this._show_erros()
                    }
                }

            } else {
                this._show_erros()
            }
            self.try_laters = 0
        },
    })
})
