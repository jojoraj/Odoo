odoo.define('lcas.evtc._functions', function(require) {
    'use strict';

    const LcasEvtcArkeup = require('evtc_front.reservations');
    const Functions = LcasEvtcArkeup.evtcArkeupMap;

    const AbstractFonctionnality = Functions.include({
        _input_value: function(query, value) {
            this._object_selector(query).value = value;
        },
        _object_selector: function(id) {
            return $(this.el).find('#' + id)[0]
        },
        _show_after: function(delay) {
            return new Promise(function(resolve) {
                setTimeout(resolve, delay);
            });
        },
        _query_selector: function(query) {
            return $('#' + query)
        },
        _center_marker: function(marker, pos) {
            marker.setPosition(pos)
            marker.setDraggable(true)
            marker.setVisible(true)
            this.googleMap.setOptions({
                center: pos,
                zoom: 16,
            });
        },
        _coordinate_object: function(lat, lng) {
            this._query_selector(lat.latitude).val(lat.value);
            this._query_selector(lng.longitude).val(lng.value);
        },
        _init_marker_window: function(text) {
            const self = this;
            self.label_info.close();
            if (!self.label_info_content) {
                self.label_info_content = self._object_selector('infowindow-content');
            }
            self.label_info.setContent(this.label_info_content);
            self.label_info_content.children["place-name"].textContent = text;
            self._show_after(200).then((value) => {
                self._query_selector('infowindow-content').css('display', 'block');
                self.label_info.open(self.googleMap, self.marker_begin_travel);
            })
        },
        _get_new_session: function() {
            return new google.maps.places.AutocompleteSessionToken()
        },
        _check_formatted_address: function(results) {
            return results.filter(res => !res.types.includes('plus_code') && !res.formatted_address.includes('+'))[0].formatted_address
        },
        _center_position: function(marker) {
            this.googleMap.setCenter(marker.getPosition());
        },
        _check_restriction_pays: function(places) {
            const mga = places.terms.filter(x => x.value.includes('Madagascar'));
            const tananarive = places.terms.filter(y => y.value.includes('Tananarive'));
            if (mga.length > 0 && tananarive.length > 0) {
                return true
            }
            return null
        },
        _onClickRecuperationButton: function(events){
            this._set_draggable_marker()
        },
        _set_draggable_marker: function() {
            this.marker_begin_travel.setDraggable(false);
        },
        _set_modify_draggable_marker: function() {
            this.marker_begin_travel.setDraggable(true);
        },
        _set_draggable_marker_destination: async function() {
            this.marker_end_travel.setDraggable(false);
        },
        _set_modify_draggable_marker_destination: function() {
            this.marker_end_travel.setDraggable(true);
        },
        _fix_marker: function(marker) {
            marker.setDraggable(false)
        },
        _addViewMap: function() {
            $('body').addClass('view-withKeyboard');
            this._remove_suggestion_value();
        },
        _removeViewMap: function(event) {
            this._remove_suggestion_value();
            $('body').removeClass('view-withKeyboard');
        },
        _remove_suggestion_value: function() {
            $('.oe_autocomplete_resume').empty();
        },
        _remove_autocompletion: function(selector_id) {
            this._query_selector(selector_id).empty();
        },
        _google_not_initialized: function(status) {
            console.info('Your browser not supported Google map or Geocode was not successful for the following reason: ' + status)
        },
        _html_object: function(selector_id, prediction, li_selector) {
            var selector = this._object_selector(selector_id)
            if (!selector || !prediction) {
                return
            }
            var html = `
                <li class="list-group-item border-0 oe_window_propagation ` + li_selector + `">
                    <table>
                        <tr>
                            <td>
                                <i class="picto picto-localisation-outline mr-2"></i>
                            </td>
                            <td>
                                <p class="p-street-recuperation " place_ids ="` + prediction.reference + `">` + prediction.description + `</p>
                            </td>
                        </tr>
                    </table>
                </li>
                `
            selector.innerHTML += html;
        },
    });
    return AbstractFonctionnality
})
