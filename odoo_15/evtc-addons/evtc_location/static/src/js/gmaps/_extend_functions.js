odoo.define('evtc_location._extendFunctions', function(require) {
    'use strict';
    const _extendFunctions = require('evtc_location.map');
    const _extend = _extendFunctions.evtcLocationMap;

    const ExtendFunctions = _extend.include({
        events: _.extend({}, _extend.prototype.events, {
            'click .oe_remove_recup_input': '_init_input_value',
            'click .oe_remove_destination_input': '_input_dest_val',
            'click .oe_remove_map_content': '_addViewMap',
            'click .oe_combine_map': '_removeViewMap',
        }),
        _init_input_value: function() {
            $(this.el).find('#address_recuperation')[0].value = '';
            this._removeViewMap();
            if (!this.marker_begin_travel) {
                return
            }
            this._remove_mail_route()
            this.marker_begin_travel.setVisible(true);
            this.marker_begin_travel.setMap(null);
            this.label_info.close();
            this._query_selector('infowindow-content').css('display', 'none');
            this._get_zoom_position(true);
        },
        _get_zoom_position: function(marker) {
            let old_marker;
            if (marker) {
                if (this.marker_end_travel) { old_marker = this.marker_end_travel.getPosition() } else { old_marker = this.TANA }
            } else if (this.marker_begin_travel) { old_marker = this.marker_begin_travel.getPosition() } else { old_marker = this.TANA }
            this.googleMap.setOptions({
                center: old_marker,
                zoom: 13,
            });
        },
        _input_dest_val: function() {
            $(this.el).find('#address_destination')[0].value = '';
            this._removeViewMap();
            if (!this.marker_end_travel) {
                return
            }
            this._remove_mail_route()
            this.marker_end_travel.setVisible(true);
            this.marker_end_travel.setMap(null);
            this.label_info_remisage.close();
            this._query_selector('infowindow-content2').css('display', 'none');
            this._get_zoom_position(false);
        },
        _remove_mail_route: function() {
            if (!this.directionsRenderer) { return }
            this.directionsRenderer.setDirections({ routes: [] });
        }
    })
    return ExtendFunctions
})
