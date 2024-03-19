odoo.define("evtc_lmfs.ShipmentTracking", function (require) {
    "use strict";

    const {ShipmentTrackingApp} = require('evtc_lmfs.ShipmentTrackingApp');
    const {ShipmentTrackingOptionsModal} = require('evtc_lmfs.options');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.ShipementTracking = publicWidget.Widget.extend({
        selector: '#oe_tracking_trip',
        events: {},

        async start() {
            this._super.apply(...arguments);
            this.trackingID = await this.getTrackingId()
            await this.initializeJourneySharing()
        },

        async getTrackingId() {
            return document.querySelector('.oe_datatracking').dataset.tracking
        },

        async initializeJourneySharing() {
            const optionsModal = new ShipmentTrackingOptionsModal('options-container');
            optionsModal.options.trackingId =  this.trackingID;
            const app = ShipmentTrackingApp.createInstance(optionsModal);
            const startTracking = this.debounce(() => {
                const trackingId = this.trackingID;
                if (trackingId !== app.trackingId) {
                    optionsModal.options.trackingId = trackingId;
                    optionsModal.saveToHistory();
                    app.trackingId = trackingId;
                }
            }, 500);
            if (this.trackingID !== "") {
                startTracking();
            }
            await app.start();
            await optionsModal.setMapView(app.mapView);
            this.remove_style_relative_in_maps(300).then(() => {
                $(this.el).find('#map_canvas')[0].style.position = ''
            })
        },

        remove_style_relative_in_maps(delay) {
            return new Promise(function (resolve) {
                setTimeout(resolve, delay);
            });
        },
        /**
         * Returns a function that will fire once at the start of [wait] ms. The
         * function will not fire again for subsequent clicks within [wait] ms of each
         * other.
         *
         * @param {!Function} func The function to debounce
         * @param {number} wait The number of ms to wait for
         * @return {!Function} The debounced function
         */
        debounce(func, wait) {
            let timeout;
            return function () {
                const context = this;
                const args = arguments;
                const callNow = !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(() => timeout = null, wait);
                if (callNow) {
                    func.apply(context, args);
                }
            };
        }
    });
    return publicWidget.registry.ShipementTracking
});
