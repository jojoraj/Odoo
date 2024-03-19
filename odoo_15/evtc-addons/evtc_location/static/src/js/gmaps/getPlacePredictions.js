odoo.define('evtc_location.PlacesServicePrediction', function(require) {
    'use strict';
    /*
        Depend @_function.js
        @params: autocompletion input
        @return: list of place for suggestion
    */
    const LcasObjectRegistry = require('evtc_location.map');
    const PlacesServicePrediction = LcasObjectRegistry.evtcLocationMap;
    let searchtimer;
    let timers;

    const RecuperationFieldsAutocomplete = PlacesServicePrediction.include({
        events: _.extend({}, PlacesServicePrediction.prototype.events, {
            'input #address_recuperation': '_delay_action',
            'click .li-street-recuperation-object': '_click_li_option',
        }),
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            this._request_call = new google.maps.places.AutocompleteService();
            return Promise.all(defs)
        },
        _delay_action: function(e) {
            clearTimeout(searchtimer);
            searchtimer = setTimeout(() => {
                var _input = e.target.value;
                if (_input.length === 0) {
                    this._remove_autocompletion('autocomplete-xd');
                    return
                }
                if (_input.length > 3) {
                    this._get_suggest_place(_input);
                }
            }, 500);
        },
        _get_suggest_place: function(input) {
            if (!input) {
                this._remove_autocompletion('autocomplete-xd');
                return
            }
            const display_all_suggestion = (predictions, status) => {
                this._remove_autocompletion('autocomplete-xd');
                if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
                    return
                }
                var place = predictions.slice(0, 5)
                place.forEach((prediction) => {
                    if (prediction.place_id || prediction.reference) {
                        this._html_object('autocomplete-xd', prediction, 'li-street-recuperation-object')
                    }
                });
            };
            const option = this.autocompleteSuggestion
            option.input = input
            this._request_call.getPlacePredictions(option, display_all_suggestion);
        },
        _click_li_option: function(li) {
            if (this.marker_begin_travel) {
                this.marker_begin_travel.setVisible(false);
                this.label_info.close();
            }
            this.marker_begin_travel.setDraggable(true);
            this.marker_begin_travel = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            var Quote = li.currentTarget.querySelector('p');
            var place_ids = Quote.attributes.place_ids.value;
            if (place_ids) {
                this._input_value('address_recuperation', Quote.innerText);
                this._remove_autocompletion('autocomplete-xd');
                new google.maps.places.PlacesService(this.googleMap).getDetails({
                        placeId: place_ids
                    },
                    (result, status) => {
                        if (status !== google.maps.places.PlacesServiceStatus.OK) {
                            this._google_not_initialized(status);
                            return;
                        }
                        this._coordinate_object({
                            'latitude': 'latitude_address_recovery',
                            'value': result.geometry.location.lat()
                        }, { 'longitude': 'longitude_address_recovery', 'value': result.geometry.location.lng() })
                        this._center_marker(this.marker_begin_travel, result.geometry.location)
                        this._init_marker_window(Quote.innerText);
                        google.maps.event.addListener(this.marker_begin_travel, 'dragend', (evt) => {
                            new google.maps.Geocoder().geocode({
                                'location': { lng: evt.latLng.lng(), lat: evt.latLng.lat() }
                            }, (results, status) => {
                                if (status === 'OK') {
                                    this.address_value = this._check_formatted_address(results);
                                    this._init_marker_window(this.address_value)
                                    this._input_value('address_recuperation', this.address_value);
                                    this._coordinate_object({
                                        'latitude': 'latitude_address_recovery',
                                        'value': evt.latLng.lat()
                                    }, { 'longitude': 'longitude_address_recovery', 'value': evt.latLng.lng() })
                                } else {
                                    this._google_not_initialized(status);
                                }
                            });
                        });
                    });
                this._removeViewMap();
            }
        },
    })
})
