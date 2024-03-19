odoo.define('evtc_location.map', function(require) {
    'use strict';

    var webPublicWidget = require('web.public.widget');
    var _registry = webPublicWidget.Widget;

    webPublicWidget.registry.evtcLocationMap = _registry.extend({
        selector: "#long-duration",
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            this.__fields();
            this.__bases();
            this.__google_callback();
            this.autocompleteSuggestion = {
                bounds: this.TANA_BOUNDS,
                strictBounds: true,
                componentRestrictions: { country: 'MG' },
            }
            return Promise.all(defs);
        },
        __selectors: function() {
            this.evtc_object = $(this.el).find('#evtc_location_maps')[0];
        },
        __bases: function() {
            this.TANA = {
                lat: -18.879293975867682,
                lng: 47.505387887452166
            };
            this.TANA_BOUNDS = {
                north: -18.620112368599735,
                south: -19.186260186571502,
                west: 46.99684105567152,
                east: 48.02543603182519,
            };
            const restriction = {
                latLngBounds: this.TANA_BOUNDS,
                strictBounds: false,
            }
            const zoom = 13;
            const openingMapOption = {
                mapTypeId: "roadmap",
                zoom: zoom,
                center: this.TANA,
                restriction: restriction,
            }
            openingMapOption.fullscreenControl = false;
            openingMapOption.streetViewControl = false;
            openingMapOption.mapTypeControl = false;
            this.options = openingMapOption;
            this.__selectors();
        },
        __pins_info: function() {
            this.label_info = new google.maps.InfoWindow();
        },
        __fields: function() {
            if ($(this.el).find('#address_recuperation').length) {
                $(this.el).find('#address_recuperation')[0].value = '';
            }
        },

        __google_callback: async function() {
            this.googleMap = await new google.maps.Map(this.evtc_object, this.options);
            this.__pins_info()
        },
    });
    return {
        evtcLocationMap: webPublicWidget.registry.evtcLocationMap
    }
})
