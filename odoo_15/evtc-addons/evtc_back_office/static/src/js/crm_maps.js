odoo.define('evtc_backOffice.opportunity_maps', function (require) {
    'use strict';

    const fieldChar = require('web.basic_fields').FieldChar;
    const fieldRegistry = require('web.field_registry');
    const core = require('web.core');
    var FormController = require('web.FormController');
    var field_utils = require('web.field_utils');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    const searchLimitationsBounds = {
        north: -18.620112368599735,
        south: -19.186260186571502,
        west: 46.99684105567152,
        east: 48.02543603182519
    }
    window.tokens = '';
    window.sessionRecuperation = 0;
    window.sessionDestination = 0;
    window.OpportunityValidate = false;
    let AwaitWhenClientisTyping;
    const autoCompleteInput = fieldChar.extend({
        supportedFieldTypes: ['char', 'text'],
        start: function () {
            this._super.apply(this, arguments);
            window.tokens = new google.maps.places.AutocompleteSessionToken();
        },
        /**
         * Compute autocomplete values
         * @override
         * @param {event}
         */
        _onInput: function (event) {
            this._super.apply(this, arguments);
            const self = this;
            clearTimeout(AwaitWhenClientisTyping);
            AwaitWhenClientisTyping = setTimeout(() => {
                const nextComponent = self.$el.next()
                const CurrentInputValue = event.target.value;
                const fieldName = this.attrs.name;
                if (CurrentInputValue.length > 3) {
                    const getPrediction = (place, status) => {
                        if (status === google.maps.places.PlacesServiceStatus.OK) {
                            self._removeQweb(nextComponent);
                            const $content = $(QWeb.render("evtc_back_office.PlacePredictionValue", {
                                uiPlaceAutocomplete: place,
                                fieldName: fieldName
                            }));
                            $($content).insertAfter(self.$el)
                        }
                    }
                    const options = {
                        input: CurrentInputValue,
                        bounds: searchLimitationsBounds,
                        strictBounds: false,
                        componentRestrictions: {country: 'MG'},
                        sessionToken: window.tokens,
                    }
                    this.placeAutocompleteService = new google.maps.places.AutocompleteService();
                    this.placeAutocompleteService.getPlacePredictions(options, getPrediction);
                } else {
                    self._removeQweb(nextComponent);
                }
            }, 500);
        },
        _removeQweb: function (nextValue) {
            if (nextValue[0]) {
                nextValue.remove()
            }
        },
    })
    fieldRegistry.add('fieldAutocompleteService', autoCompleteInput);

    FormController.include({
        events: _.extend({}, FormController.prototype.events, {
            'click .oe_place_li_st': '_onPlaceService',
        }),
        _OnTriggerUp: function (results, field) {
            const generator = results[0].geometry.location
            if (field === 'pick_up_zone') {
                $('input[name="pick_up_lat"]').val(generator.lat()).change();
                $('input[name="pick_up_long"]').val(generator.lng()).change();
                window.sessionRecuperation++;
            } else if (field === 'destination_zone') {
                $('input[name="dest_lat"]').val(generator.lat()).change();
                $('input[name="dest_long"]').val(generator.lng()).change();
                window.sessionDestination++;
            }
        },
        _onPlaceService: async function (event) {
            const Target = event.target
            const placeId = Target.attributes.place_id.value;
            const text = Target.innerText;
            const field = Target.offsetParent.attributes.field.value
            const $sel = $('input[name=' + field + ']');
            $sel.val(text).focus().change();
            $sel.next()[0].remove();
            const geocoder = new google.maps.Geocoder();
            const rpmResult = geocoder.geocode({placeId: placeId})
            await rpmResult.then(({results}) => {
                if (results) {
                    this._OnTriggerUp(results, field)
                } else {
                    console.info("No results found");
                }
            })
            rpmResult.catch((e) => console.error("Geocoder failed due to: " + e));
            const pick_lat = $('input[name="pick_up_lat"]').val(),
                pick_lng = $('input[name="pick_up_long"]').val(),
                dest_lat = $('input[name="dest_lat"]').val(),
                dest_lng = $('input[name="dest_long"]').val()
            if (pick_lat && pick_lng && dest_lat && dest_lng) {
                const option = {
                    origin: new google.maps.LatLng(pick_lat, pick_lng),
                    destination: new google.maps.LatLng(dest_lat, dest_lng),
                    travelMode: 'DRIVING'
                }
                const request = new google.maps.DirectionsService().route(option);
                await request.then((response) => {
                    const result = response.routes[0].legs[0]
                    const km = result.distance.value; // In metters
                    const tim = result.duration.value; //  In seconds
                    const distance = (km / 1000).toString().replace('.', ',');
                    $('input[name="estimated_kilometers"]').val(distance).focus().change();
                    const fields_ = field_utils.format.float_time(tim / 3600)
                    $('input[name="duration"]').val(fields_).focus().change();
                });
                request.catch((e) => console.info("Directions request failed due to " + e));
            }
            window.tokens = new google.maps.places.AutocompleteSessionToken();
        },
        _onSave: function () {
            if (this.modelName === 'crm.lead' &&
                (window.sessionRecuperation || window.sessionDestination) ) {
                window.OpportunityValidate = true;
                const data = {
                    'recuperation': window.sessionRecuperation,
                    'destination': window.sessionDestination,
                    'isValidate': window.OpportunityValidate,
                };
                ajax.jsonRpc('/session-log', 'call', data)
                window.sessionRecuperation = 0;
                window.sessionDestination = 0;
                window.OpportunityValidate = false;
            }
            this._super.apply(this, arguments);
        },
        _onDiscard: function () {
            if (this.modelName === 'crm.lead' &&
                (window.sessionRecuperation || window.sessionDestination) ) {
                const data = {
                    'recuperation': window.sessionRecuperation,
                    'destination': window.sessionDestination,
                    'isValidate': window.OpportunityValidate,
                };
                ajax.jsonRpc('/session-log', 'call', data)
                window.sessionRecuperation = 0;
                window.sessionDestination = 0;
            }
            this._super.apply(this, arguments);
        }
    });
})
