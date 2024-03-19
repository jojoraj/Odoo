odoo.define('vtc_area_destination.new_destination', function(require) {
    'use strict';

    const vtcMap = require('evtc_front.reservations')

    vtcMap.evtcArkeupMap.include({

        events: _.extend({}, vtcMap.evtcArkeupMap.prototype.events, {
            'click #add_destination': '_onClickDestination',
        }),

        start: async function() {
            await this._super.apply(this, arguments)
        },

        _catch_errors: function(longitude, latitude, input) {
            return Boolean(latitude) && Boolean(longitude) && Boolean(input[0].value)
        },

        _onClickDestination: async function(onInput = true, onInsert = false) {
            const mainInput = $(this.el).find('#address_destination')
            const hasObject = {
                modification_id: 0,
                lat: this.$('input#latitude_address_destination')[0].value,
                lng: this.$('input#longitude_address_destination')[0].value,
                status: 'draft',
                hasRegister: this._init_destination(false),
                isUpdate: false,
            }
            const params = await this._get_params(hasObject)
            if (params.status) {
                if (mainInput[0] && !this._catch_errors(hasObject.lng, hasObject.lat, mainInput)) {
                    this._show_erros()
                    return
                }
                this._remove_all_errors_message()
                if (onInsert) {
                    this._appendQweb(this.txContext.selector.mainXmlClass, this.txContext.selector.getXmlID, params)
                    this._toggle_add_destination()
                } else {

                    if (this.on_first_destination) {
                        hasObject.status = 'new';
                        const newParams = this._get_params(hasObject)
                        this._createLiOption(newParams)
                        this.on_first_destination = false
                            // Remove li option
                        const autoCompletion = this.$('#autocomplete-x1dCV')[0]
                        if (autoCompletion) {
                            autoCompletion.remove()
                        }
                        // Create marker
                        if (this.transientMarker.length > 0) {
                            this.txContext.destination.slice(-1)[0].marker = this.transientMarker.slice(-1)[0]
                            this.transientMarker = []
                        }
                        await this._reorderSequence()
                    }

                    this._is_destinationInput()

                    if (onInput) {
                        this._appendQweb(this.txContext.selector.mainXmlClass, this.txContext.selector.getXmlID, params)
                        this._toggle_add_destination()
                        this._disable_modification()
                    }


                    this.txContext.destinationMode = 'new';
                    this.initialized_coordinate_value();
                    this.marker_end_travel = new google.maps.Marker({
                        icon: "/evtc_front/static/src/images/marker/trip.svg",
                        map: this.googleMap,
                        draggable: true,
                    });
                }
            }
        },
    })
})
