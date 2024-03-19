odoo.define('object.modal_maps', function (require) {
    'use strict';
    const publicWidget = require('web.public.widget');
    publicWidget.registry.modalMaps = publicWidget.Widget.extend({
        selector: '#oe_map_integration_tmpl',
        start: function () {
            this.TANA = {lat: -18.879293975867682, lng: 47.505387887452166};
            this.TANA_BOUNDS = {
                north: -18.620112368599735,
                south: -19.186260186571502,
                west: 46.99684105567152,
                east: 48.02543603182519,
            };
            try {
                if (this.ModalGooglemap){
                    this.window_info.close();
                    this.modalMarker.setVisible(false);
                }
                else {
                    this._showMaps();
                }
            }
            catch (e) {}
        },
        _check_formatted_address: function (results) {
            return results.filter(res => !res.types.includes('plus_code') && !res.formatted_address.includes('+'))[0].formatted_address
        },
        _showMaps: function () {
            this.divContent = $(this.el).find('#modal_maps_adress')[0];
            if (!this.divContent) {
                return
            }
            this.ModalGooglemap = new google.maps.Map(this.divContent, {
                mapTypeId: "roadmap", zoom: 13, center: this.TANA,
                fullscreenControl: false, streetViewControl: false, mapTypeControl: false,
                restriction: {latLngBounds: this.TANA_BOUNDS, strictBounds: false},
            });
            this.modalMarker = new google.maps.Marker({map: this.ModalGooglemap, draggable: true,});
            // Initialise info window content
            this.window_info = new google.maps.InfoWindow();
            this.Place_name_content = $(this.el).find('#markerInfo')[0];
            this.window_info.setContent(this.Place_name_content);
        },
    })
    return {
        ModalMaps: publicWidget.registry.modalMaps
    };
})
