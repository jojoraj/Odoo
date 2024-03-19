odoo.define('vtc_area_destination.to_delete', function(require) {
    'use strict';

    const vtcMap = require('evtc_front.reservations')

    vtcMap.evtcArkeupMap.include({

        events: _.extend({}, vtcMap.evtcArkeupMap.prototype.events, {
            'click .to-delete': '_deleteAddress',
        }),

        start: async function() {
            await this._super.apply(this, arguments)
        },

        _deleteAddress: async function(events) {
            const current_identifier_id = this.render_selector_id(events.currentTarget.parentNode.attributes.id.value)
            const custom = this._filter_li_data(current_identifier_id)
            this.txContext.destination.filter(y => y.id === current_identifier_id).forEach(z => {
                z.marker.marker.setVisible(false)
                z.marker.marker.setMap(null)
                z.marker.label.close()
            })
            this.txContext.destination = this.txContext.destination.filter(z => z.id !== current_identifier_id)
                // Remove li DOM
            custom.remove()
                // End of DOM remove
            this.transientMarker = []
            if (this.txContext.destination.length < 1) {
                this.marker_end_travel = new google.maps.Marker({
                    icon: "/evtc_front/static/src/images/marker/trip.svg",
                    map: this.googleMap,
                    draggable: true,
                });
            }
            await this._reorderSequence()
            if (this.txContext.destination.length > 0) {
                this.marker_end_travel = this.txContext.destination.slice(-1)[0].marker.marker
            }

            if (this.txContext.destination.length < 1) {
                this._onClickDestination(true, true)
            }

            this._toggle_add_destination()
        },
    })
})
