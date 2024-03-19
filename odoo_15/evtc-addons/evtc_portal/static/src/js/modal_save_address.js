odoo.define('myadress.evtc.map', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    let searchtimer;
    publicWidget.registry.saveAdress = publicWidget.Widget.extend({
        selector: '.oe_portal_map_address',
        events: {
            'input #input_partner_street': '_after',
            'click .open-modal-address': '_OnClickOpenModalAddress',
            'click .p-street-recuperation': '_OnClickStreetRecuperation',
            'click .delete_contact': '_OnClickDeleteContact',
            'click .oe_remove_next_chiild': '_delete_next_input',
        },
        init: function () {
            this.ModalGooglemap = null;
            this.modalMarker = null;
            this.active_id = null;
        },
        start: function () {
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
            this.active_id = null;
            this.options = {
                bounds: this.TANA_BOUNDS,
                strictBounds: true,
                componentRestrictions: {country: 'MG'},
            }
        },
        remove_marker: function () {
            if (this.modalMarker) {
                this.modalMarker.setVisible(false);
                this.infowindow.close();
            }
        },
        get_marker: function () {
            this.modalMarker.setDraggable(true);
            this.modalMarker = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.ModalGooglemap,
                draggable: true,
            });
        },
        _delete_next_input: function () {
            $('#input_partner_street').val('');
            this.remove_marker();
            this.get_marker();
        },
        _init_items_details: function (event) {
            if (this.data_option === 'save') {
                $('.on-save-address').show();
                this.contact_id = event.target.dataset.id;
                if (event.target.dataset.name) {
                    this.$('#partner_name')[0].value = event.target.dataset.name;
                }
                this.contact_lat = parseFloat(event.target.dataset.lat);
                this.contact_lng = parseFloat(event.target.dataset.lng);
                this.$('#contact_id')[0].value = this.contact_id;
                this._init_input(event.target.dataset.street, event.target.dataset.lat, event.target.dataset.lng);
            }
            if (this.data_option === 'add') {
                $('.on-add-address').show();
            }
        },
        _initialized_session_token: function () {
            if (this.sessionToken) {
                return this.sessionToken
            }
            return this._get_new_session();
        },
        _get_new_session: function () {
            return new google.maps.places.AutocompleteSessionToken()
        },
        _init_input: function (address_value, new_lat, new_long) {
            this.address_value = address_value;
            this.$('#input_partner_street')[0].value = address_value;
            this.$('#new_addr_lat')[0].value = new_lat;
            this.$('#new_addr_long')[0].value = new_long;
        },
        _reset_data: function () {
            this.data_option = null;
            this._init_input("", "", "");
            $('.on-add-address').hide();
            $('.modal-title').hide();
            $('#partner_name').val('');
            if (this.ModalGooglemap) {
                this.ModalGooglemap = null;
                this.modalMarker = null;
                this.infowindow = null;
            }
        },
        _OnClickOpenModalAddress: function (event) {
            this._reset_data();
            this.data_option = event.target.dataset.option;
            this._init_items_details(event);
            $('#modal_maps_adress').empty();
            $('#modal_save_contact_address').modal('show');
            this._showMaps('modal_maps_adress');
        },
        _OnClickStreetRecuperation: function (event) {
            const data = {
                'place_id': event.target.dataset.placeId,
                'place_name': event.currentTarget.textContent
            }
            this._geocode_location_place_id(data);
            this.sessionToken = this._get_new_session()
        },
        _showMaps: function (element) {
            if (!document.getElementById(element)) {
                return
            }
            $("#markerInfo").css('display', 'none');
            this.ModalGooglemap = new google.maps.Map(document.getElementById(element), {
                mapTypeId: "roadmap",
                zoom: 10,
                center: this.TANA,
                fullscreenControl: false,
                streetViewControl: false,
                mapTypeControl: false,
                restriction: {
                    latLngBounds: this.TANA_BOUNDS,
                    strictBounds: true
                },
            });
            this.modalMarker = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.ModalGooglemap,
                position: this.TANA,
                draggable: true,
            });
            this.infowindow = new google.maps.InfoWindow();
            this._later(1500).then((value) => {
                if (this.data_option === 'add') {
                    this._get_my_position();
                }
                if (this.data_option === 'save') {
                    const pos = {
                        lat: this.contact_lat,
                        lng: this.contact_lng
                    };
                    this._center_on_position(pos, 16);
                    this._init_window(this.$('#input_partner_street')[0].value)
                }
                google.maps.event.addListener(this.modalMarker, 'dragend', (evt) => {
                    new google.maps.Geocoder().geocode({
                        'location': {
                            lng: evt.latLng.lng(),
                            lat: evt.latLng.lat()
                        }
                    }, (results, status) => {
                        if (status === 'OK') {
                            this.address_value = this._check_formatted_address(results);
                            this.$('#input_partner_street')[0].value = this.address_value;
                            this.$('#new_addr_lat')[0].value = evt.latLng.lat();
                            this.$('#new_addr_long')[0].value = evt.latLng.lng();
                            this._init_input(this._check_formatted_address(results), evt.latLng.lat(), evt.latLng.lng())
                            this._init_window(this.address_value);
                        }
                    });
                });
            })

        },
        _later: function (delay) {
            return new Promise(function (resolve) {
                setTimeout(resolve, delay);
            });
        },
        _center_on_position: function (pos, zoom) {
            this.modalMarker.setPosition(pos);
            this.ModalGooglemap.setCenter(pos);
            this.ModalGooglemap.setZoom(zoom);
        },
        _get_my_position: function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const pos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                        };
                        this._center_on_position(pos, 16, 'Your current location');
                        this._geocode_location(pos);
                    },
                    () => {
                        handleLocationError(true, this.infowindow, this.ModalGooglemap.getCenter());
                    }
                );
            } else {
                // Browser doesn't support Geolocation
                handleLocationError(false, this.infowindow, this.ModalGooglemap.getCenter());
            }
        },
        handleLocationError: function (browserHasGeolocation, infoWindow, pos) {
            infoWindow.setPosition(pos);
            infoWindow.setContent(
                browserHasGeolocation ?
                    "Error: The Geolocation service failed." :
                    "Error: Your browser doesn't support geolocation."
            );
            infoWindow.open(map);
        },
        _get_selector: function (id = '', name = '', natif = false) {
            if (natif) {
                return id ? $('#' + id) : $('.' + name)
            }
            return id ? $(this.el).find('#' + id)[0] : $(this.el).find('.' + name)[0]
        },
        _remove_html: function (selector, jquery) {
            var object = this._get_selector(selector, '', jquery);
            if (object) {
                object.empty()
            }
        },
        _autocomplete_html: function (selector_id, value) {
            var selector = this._get_selector(selector_id, '', false)
            if (!selector || !value) {
                return
            }
            var html = `
                <li class="list-group-item border-0 my-account-add-adress col-10">
                    <table>
                        <tr>
                            <td>
                                <i class="picto picto-address-black mr-2"></i>
                            </td>
                            <td>
                                <p class="p-street-recuperation" data-place-id="` + value.reference + `">` + value.description + `</p>
                            </td>
                        </tr>
                    </table>
                </li>
                `
            selector.innerHTML += html;
        },
        _after: function (values) {
            clearTimeout(searchtimer);
            searchtimer = setTimeout(() => {
                var data = values.target.value;
                if (data.length > 3) {
                    this._OnInputPartnerStreet(values);
                }
            }, 500);
        },
        _OnInputPartnerStreet: function (type) {
            var object = $("#input_partner_street").val();
            if (!object) {
                this._remove_html('add-adress-xd', true);
                return
            }
            const displaySuggestions = (predictions, status) => {
                this._remove_html('add-adress-xd', true);
                if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
                    $('<li class="list-group-item border-0 li-street-recuperation col-10"><table><tr><td></td><td><p class="p-street-recuperation"> No results </p></td></tr></table></li>').appendTo(this.auto_com)
                    return
                }
                var predo = predictions.slice(0, 5)
                predo.forEach((prediction) => {
                    if (prediction.reference) {
                        this._autocomplete_html('add-adress-xd', prediction)
                    }
                });
            };
            const option = this.options
            option.input = object;
            const service = new google.maps.places.AutocompleteService();
            service.getPlacePredictions(option, displaySuggestions);
        },
        _check_formatted_address: function (results) {
            return results.filter(res => !res.types.includes('plus_code') && !res.formatted_address.includes('+'))[0].formatted_address
        },
        _init_window: function (name) {
            this._later(300).then((value) => {
                var element = $(this.el).find('#Place-name-content')[0];
                if (element) {
                    element.textContent = name;
                } else {
                    this._create_window(name);
                }
                this.place_name_adress = $(this.el).find('#markerInfo')[0];
                this.infowindow.setContent(this.place_name_adress);
                // This.place_name_adress.children["Place-name-content"].textContent = name;
                // var redis = document.getElementById('Place-name-content');
                this.infowindow.open(this.ModalGooglemap, this.modalMarker);
                $("#markerInfo").css('display', 'block');
            })
        },
        _create_window: function (name) {
            var div = `
                        <div id="markerInfo" style="display:none !important;">
                          <span id="Place-adress-content">
                            <img class="mr-1 svg-size" src="/evtc_portal/static/src/img/icon-label.svg"/>
                          </span>
                          <span id="Place-name-content" class="title Place-name-content">` + name + `</span>
                          <br/>
                        </div>
                    `
            document.getElementById('modal_maps_adress').insertAdjacentHTML('afterend', div)
        },
        _geocode_location: function (pos) {
            new google.maps.Geocoder().geocode({
                'location': pos
            }, (results, status) => {
                if (status === 'OK') {
                    this.address_value = this._check_formatted_address(results);
                    this._init_input(this._check_formatted_address(results), pos.lat, pos.lng)
                    this._init_window(this.address_value)
                }
            });
        },
        _geocode_location_place_id: function (data) {
            const place_id = data.place_id;
            const place_name = data.place_name;
            new google.maps.Geocoder().geocode({
                placeId: place_id
            }, (results, status) => {
                if (status === 'OK') {
                    const pos = {
                        lat: results[0].geometry.location.lat(),
                        lng: results[0].geometry.location.lng()
                    };
                    this._init_input(place_name, results[0].geometry.location.lat(), results[0].geometry.location.lng());
                    this._init_window(place_name);
                    $('#add-adress-xd').empty();
                    this._center_on_position(pos, 16)
                }
            });
        },
        _OnClickDeleteContact: function (event) {
            $.ajax({
                type: "POST",
                url: '/my/contact/delete',
                data: {'contact_id': $('#contact_id').val()}
            }).then(() => {
                location.reload();
            });
        },

    })
    return {
        saveModalAdress: publicWidget.registry.saveAdress
    }
})
