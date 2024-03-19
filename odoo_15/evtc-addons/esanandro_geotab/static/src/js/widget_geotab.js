odoo.define('map_geotab', function(require, factory) {
    // 'use strict';
    // var Widget = require('web.Widget');
    // var rpc = require('web.rpc');
    // var ajax = require('web.ajax');

    // $(document).ready(function() {
    //     var routingControl = [];
    //     var oIconGreen = L.divIcon({
    //         iconAnchor: [15, 15],
    //         className: 'circle-marker',
    //         html: '<div class="circle-animate circle circle-green"></div>'
    //     });
    //     var oIconRed = L.divIcon({
    //         iconAnchor: [15, 15],
    //         className: 'circle-marker',
    //         html: '<div class="circle-animate circle circle-red"></div>'
    //     });
    //     var map = L.map('map', {
    //         center: [-18.9102, 47.5255],
    //         zoom: 13
    //     });

    //     function get_trip_route() {
    //         var data = JSON.parse(localStorage.getItem('coordinate'));
    //         if (data) {
    //             var xa = data['xa'];
    //             var ya = data['ya'];
    //             var xd = data['xd'];
    //             var yd = data['yd'];
    //             if (xd, yd, xa, ya) {
    //                 get_zone_coordonate($('#pickupPoint_zone').val(), $('#pickbackPoint_zone').val());
    //                 localStorage.removeItem('coordinate');
    //             }
    //         }
    //     }
    //     L.Map.include({
    //         getMarkerById: function(id) {
    //             var marker = null;
    //             this.eachLayer(function(layer) {
    //                 if (layer instanceof L.Marker) {
    //                     if (layer.options.custmID === id) {
    //                         marker = layer;
    //                     }
    //                 }
    //             });
    //             return marker;
    //         }
    //     });
    //     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
    //     var BeginMarquer;
    //     $('#pickupPoint_zone').focusout(function() {
    //         var pickupZone = $("#pickupPoint_zone").val();
    //         if (pickupZone) {
    //             ajax.jsonRpc('/web/geotab/marker', 'call', { 'address': pickupZone })
    //                 .then(function(result) {
    //                     var x = result['x'];
    //                     var y = result['y'];
    //                     var layersID = map.getMarkerById(1);
    //                     if (layersID) {
    //                         map.removeLayer(layersID);
    //                     }
    //                     BeginMarquer = L.marker([y, x], { icon: oIconGreen, custmID: 1, title: 'begin', draggable: true });
    //                     BeginMarquer.addTo(map);
    //                     map.setView([y, x], 14);
    //                     // create localstorage point
    //                     var data = localStorage.getItem('coordinate');
    //                     var data_type = JSON.parse(data);
    //                     if (!data_type) {
    //                         data_type = { 'xa': NaN, 'ya': NaN, 'xd': NaN, 'yd': NaN }
    //                     }
    //                     data_type['xd'] = x;
    //                     data_type['yd'] = y;
    //                     BeginMarquer.on('dragend', function(event) {
    //                         var marker = event.target;
    //                         var position = marker.getLatLng();
    //                         ajax.jsonRpc('/web/geotab/new/latLng', 'call', { 'latLng': position }).then(function(arg) {
    //                             $("#pickupPoint_zone").val(arg);
    //                             var pickup = arg;
    //                             var pickback = $('#pickbackPoint_zone').val();
    //                             if (pickup && pickback) {
    //                                 get_zone_coordonate(pickup, pickback);
    //                             }
    //                         })
    //                     });
    //                     // store in localstorage
    //                     localStorage.setItem('coordinate', JSON.stringify(data_type));
    //                     get_trip_route();
    //                 });
    //         }
    //     });

    //     $('#pickbackPoint_zone').focusout(function() {
    //         var pickupZone = $("#pickbackPoint_zone").val();
    //         if (pickupZone) {
    //             ajax.jsonRpc('/web/geotab/marker', 'call', { 'address': pickupZone })
    //                 .then(function(result) {
    //                     var x = result['x'];
    //                     var y = result['y'];
    //                     var layersID = map.getMarkerById(2);
    //                     if (layersID) {
    //                         map.removeLayer(layersID);
    //                     }
    //                     var endMarquer = L.marker([y, x], { icon: oIconRed, custmID: 2, title: 'stop', draggable: true });
    //                     endMarquer.addTo(map);
    //                     map.setView([y, x], 14);
    //                     var data = localStorage.getItem('coordinate');
    //                     var data_type = JSON.parse(data);
    //                     if (!data_type) {
    //                         data_type = { 'xa': NaN, 'ya': NaN, 'xd': NaN, 'yd': NaN }
    //                     }
    //                     data_type['xa'] = x;
    //                     data_type['ya'] = y;
    //                     // store in localstorage
    //                     endMarquer.on('dragend', function(event) {
    //                         var marker = event.target;
    //                         var position = marker.getLatLng();
    //                         ajax.jsonRpc('/web/geotab/new/latLng', 'call', { 'latLng': position }).then(function(arg) {
    //                             // document.getElementById("pickupPoint_zone").innerHTML = arg;
    //                             $("#pickbackPoint_zone").val(arg);
    //                             // get_zone_coordonate($('#pickupPoint_zone').val(), $('#pickbackPoint_zone').val());
    //                             var pickup = $('#pickupPoint_zone').val();
    //                             var pickback = arg;
    //                             if (pickup && pickback) {
    //                                 get_zone_coordonate(pickup, pickback);
    //                             }
    //                         })
    //                     });
    //                     localStorage.setItem('coordinate', JSON.stringify(data_type));
    //                     get_trip_route();
    //                 });
    //         }
    //     });

    // });

    // function get_zone_coordonate(pickup_point, storage_point) {
    //     if (storage_point, pickup_point) {
    //         ajax.jsonRpc('/web/get-coordonate-description/', 'call', { 'coordinate': [pickup_point, storage_point] }).then(function(coordinate) {
    //             if (coordinate) {
    //                 var data = JSON.parse(localStorage.getItem('geotab'));
    //                 const point = coordinate[0];
    //                 const trip = coordinate[1];
    //                 if (point && data) {
    //                     data['pickup_point'] = point[0];
    //                     data['storage_point'] = point[1];
    //                 }
    //                 if (trip && data) {
    //                     data['distance'] = trip[0];
    //                     data['duration'] = trip[1];
    //                 }
    //                 localStorage.removeItem('geotab');
    //                 localStorage.setItem('geotab', JSON.stringify(data));
    //                 change_duration_distance(trip[0], trip[1]);
    //             }
    //         });
    //     }
    // }
    // $('#create-validation').on('click', function() {
    //     var d = JSON.parse(localStorage.getItem('geotab'));
    //     d['vehicle'] = $("#vehicle-action").val();
    //     ajax.jsonRpc('/web/vehicle-create', 'call', { 'data': d }).then(function(result) {
    //         if (result) {
    //             location.reload();
    //         }
    //     });
    // });

    // function change_duration_distance(distance, duration) {
    //     if (distance && duration) {
    //         $('#strip-distance').empty();
    //         $('#strip-duration').empty();
    //         $("#strip-distance").val(distance + ' Km');
    //         $("#strip-duration").val(duration + ' ')
    //     }
    // };
});
