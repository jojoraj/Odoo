// Odoo.define('geotab_frontend', function(require) {
//     'use strict';
//     var Widget = require('web.Widget');
//     var rpc = require('web.rpc');
//     var ajax = require('web.ajax');

//     $(document).ready(function() {
//         var $array = ['a', 'e', 'i'];
//         var stor = localStorage.getItem('geotab');
//         if (stor) {
//             hide_all_information();
//         }

//         function get_autocomplete_array(values) {
//             ajax.jsonRpc('/web/geotab-check-point/', 'call', { 'data': values }).then(function(arr) {
//                 for (let index = 0; index < arr.length; index++) {
//                     const element = arr[index];
//                     $array.push(element);
//                 }
//             })
//             return $array;
//         }
//         $(function() {
//             $('#delivery_date').datetimepicker();
//         });

//         $("#pickup_point").on('input', function(e) {
//             var pickup_text = $('#pickup_point');
//             // var suggest_list = get_autocomplete_array(pickup_text.val());
//             // autocomplete(document.getElementById("pickup_point"));
//         });
//         $("#storage_point").on('input', function(e) {
//             var storage_text = $('#storage_point');
//             var suggest_list = get_autocomplete_array(storage_text.val());
//             autocomplete(document.getElementById("storage_point"));
//         });

//         function autocomplete(inp) {
//             var arr = $array;
//             var currentFocus;
//             inp.addEventListener("input", function(e) {
//                 var a, b, i, val = this.value;
//                 closeAllLists();
//                 if (!val) { return false; }
//                 currentFocus = -1;
//                 a = document.createElement("DIV");
//                 a.setAttribute("id", this.id + "autocomplete-list");
//                 a.setAttribute("class", "autocomplete-items");
//                 this.parentNode.appendChild(a);
//                 for (i = 0; i < arr.length; i++) {
//                     if (arr[i].substr(0, val.length).toUpperCase() === val.toUpperCase()) {
//                         b = document.createElement("DIV");
//                         b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
//                         b.innerHTML += arr[i].substr(val.length);
//                         b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
//                         b.addEventListener("click", function(e) {
//                             inp.value = this.getElementsByTagName("input")[0].value;
//                             closeAllLists();
//                         });
//                         a.appendChild(b);
//                     }
//                 }
//             });
//             inp.addEventListener("keydown", function(e) {
//                 var x = document.getElementById(this.id + "autocomplete-list");
//                 if (x) x = x.getElementsByTagName("div");
//                 if (e.keyCode === 40) {
//                     currentFocus++;
//                     addActive(x);
//                 } else if (e.keyCode === 38) {
//                     currentFocus--;
//                     addActive(x);
//                 } else if (e.keyCode === 13) {
//                     e.preventDefault();
//                     if (currentFocus > -1) {
//                         if (x) x[currentFocus].click();
//                     }
//                 }
//             });

//             function addActive(x) {
//                 if (!x) return false;
//                 removeActive(x);
//                 if (currentFocus >= x.length) currentFocus = 0;
//                 if (currentFocus < 0) currentFocus = (x.length - 1);
//                 x[currentFocus].classList.add("autocomplete-active");
//             }

//             function removeActive(x) {
//                 for (var i = 0; i < x.length; i++) {
//                     x[i].classList.remove("autocomplete-active");
//                 }
//             }

//             function closeAllLists(elmnt) {
//                 var x = document.getElementsByClassName("autocomplete-items");
//                 for (var i = 0; i < x.length; i++) {
//                     if (elmnt != x[i] && elmnt != inp) {
//                         x[i].parentNode.removeChild(x[i]);
//                     }
//                 }
//             }
//             document.addEventListener("click", function(e) {
//                 closeAllLists(e.target);
//             });
//         };

//         $("#to-vehicle").on('click', function() {
//             var reservation_id = $('#tarif-action').val();
//             localStorage.setItem('session_tarif', JSON.stringify({ 'session_id': reservation_id }))
//             ajax.jsonRpc('/web/vehicle-related-tarif', 'call', { 'reservation_id': reservation_id }).then(function(reserv) {
//                 for (let index = 0; index < reserv.length; index++) {
//                     const vehicle = reserv[index];
//                     var mess = 'place';
//                     if (vehicle['seat'] > 1) {
//                         mess = 'places';
//                     }
//                     var text = vehicle['name'] + ' ' + vehicle['color'] + ' (' + vehicle['seat'] + ' ' + mess + ')';
//                     var opt = document.createElement('option');
//                     opt.value = vehicle['fleet_id'];
//                     opt.innerHTML = text;
//                     document.getElementById("vehicle-action").appendChild(opt);
//                 }
//                 get_first_information();
//                 get_zone_coordonate($('#pickup_point').val(), $('#storage_point').val());
//                 setTimeout(() => {
//                     hide_all_information();
//                 }, 5000);
//             });
//         });

//         function change_duration_distance(distance, duration) {
//             var info = JSON.parse(localStorage.getItem('geotab'));
//             if (distance && duration) {
//                 console.log(distance, duration)
//                 $('#strip-distance').empty();
//                 $('#strip-duration').empty();
//                 // create values
//                 document.getElementById("strip-distance").innerHTML = distance + ' Km'
//                 document.getElementById("strip-duration").innerHTML = duration + ' '
//             }
//         }

//         function get_zone_coordonate(pickup_point, storage_point) {
//             ajax.jsonRpc('/web/get-coordonate-description/', 'call', { 'coordinate': [pickup_point, storage_point] }).then(function(coordinate) {
//                 if (coordinate) {
//                     var data = JSON.parse(localStorage.getItem('geotab'));
//                     const point = coordinate[0];
//                     const trip = coordinate[1];
//                     if (point && data) {
//                         data['pickup_point'] = point[0];
//                         data['storage_point'] = point[1];
//                     }
//                     if (trip && data) {
//                         data['distance'] = trip[0];
//                         data['duration'] = trip[1];
//                     }
//                     localStorage.removeItem('geotab');
//                     localStorage.setItem('geotab', JSON.stringify(data));
//                     change_duration_distance(trip[0], trip[1]);
//                 }
//             });
//         }
//         $('#return-info').on('click', function() {
//             return_all_info();
//             remove_first_information();
//         })

//         function remove_first_information() {
//             localStorage.removeItem('geotab');
//             // store value in locaStorage
//         }

//         function get_first_information() {
//             var phone = $('#phone').val();
//             var delivery_date = $('#delivery_date').data()['date'];
//             var pickup_point = $('#pickup_point').val();
//             var storage_point = $('#storage_point').val();
//             var data = {
//                 'delivery_date': delivery_date,
//                 'pickup_point': pickup_point,
//                 'phone': phone,
//                 'storage_point': storage_point
//             };
//             var item = localStorage.getItem('session_tarif')
//             if (item) {

//             }
//             localStorage.setItem('geotab', JSON.stringify(data));
//         }

//         function hide_all_information() {
//             // hide appropriate div
//             $(".att-vehicle-remove").css("display", 'none');
//             // show appropriate div
//             $('.att-vehicle-show').show();
//             $('.procces-btn').text('Valider');
//         }

//         function return_all_info() {
//             // hide appropriate div
//             $(".att-vehicle-show").css("display", 'none');
//             // show appropriate div
//             $('.att-vehicle-remove').show();
//             $('.procces-btn').text('Suivant');
//         }

//         $('#own-reservation').on('click', function() {
//             show_own_reservation();
//         });
//         $('#new-reservation').on('click', function() {
//             show_new_reservation();
//         });

//         function show_own_reservation() {
//             // remove geotab in localstorage & create own reservation value
//             var geotab = localStorage.getItem('geotab');
//             if (geotab) { localStorage.removeItem('geotab') }
//             var $data = {
//                 'own_reservation': true
//             }
//             localStorage.setItem('own_reservation', JSON.stringify($data));
//             // remove all views
//             $('.att-vehicle-remove').css('display', 'none');
//             $('.att-vehicle-show').css('display', 'none');
//             // show own-résérvation
//             $('#own-reservation-block').show();
//             $('.map-view').hide();
//             $('.resvn-wd').css('width', '100%')
//         };

//         function show_new_reservation() {
//             // remove geotab in localstorage & create own reservation value
//             var reserv = localStorage.getItem('own_reservation');
//             if (reserv) { localStorage.removeItem('own_reservation') }

//             // remove all views
//             $('.att-vehicle-remove').css('display', 'block');
//             $('.att-vehicle-show').css('display', 'none');
//             // show own-résérvation
//             $('#own-reservation-block').hide();
//             $('.map-view').show();
//             $('.resvn-wd').css('width', '40%')
//         };

//         // var marker = null;
//         // // var map = L.map('map').setView([-18.9102, 47.5255], 12);
//         // var map = L.map('map', {
//         //     center: [-18.9102, 47.5255],
//         //     zoom: 13
//         // });
//         // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);

//         // function placerMarqueur(e, address, state) {
//         //     var x = e['x'];
//         //     var y = e['y']
//         //     var z = L.latLng(e['x'], e['y'])
//         //     if (state) {
//         //         L.marker([y, x]).addTo(map).bindPopup('Départ: ' + address).openPopup();
//         //     } else {
//         //         L.marker([y, x]).addTo(map).bindPopup('Arrivé: ' + address).openPopup();
//         //     }
//         //     var ss = JSON.parse(localStorage.getItem('bounds'));
//         //     if (ss) {
//         //         if (ss['depart'] && ss['arrive']) {
//         //             var d = ss['depart'];
//         //             var a = ss['arrive'];
//         //             L.Routing.control({
//         //                 waypoints: [
//         //                     L.latLng(d[0], d[1]),
//         //                     L.latLng(a[0], a[1])
//         //                 ],
//         //                 autoRoute: true,
//         //                 routeWhileDragging: true,
//         //             }).addTo(map);

//         //             // zoom the map to the polyline
//         //             // map.fitBounds(polyline.getBounds());
//         //             localStorage.setItem('bounds', JSON.stringify({}));
//         //         }
//         //     }
//         //     map.setView([y, x], 15);
//         // }

//         // $('#pickup_point').focusout(function() {
//         //     var rec = $("#pickup_point").val();
//         //     if (rec) {
//         //         ajax.jsonRpc('/web/geotab/marker', 'call', { 'address': rec })
//         //             .then(function(result) {
//         //                 var store = localStorage.getItem('bounds');
//         //                 var data = JSON.parse(store)
//         //                 if (!data) {
//         //                     data = {}
//         //                 }
//         //                 data['depart'] = [result['y'], result['x']]
//         //                 localStorage.setItem('bounds', JSON.stringify(data))
//         //                 placerMarqueur(result, rec, true);
//         //             });
//         //     }
//         // });
//         // $('#storage_point').focusout(function() {
//         //     var rec = $("#storage_point").val();
//         //     if (rec) {
//         //         ajax.jsonRpc('/web/geotab/marker', 'call', { 'address': rec })
//         //             .then(function(result) {
//         //                 var store = localStorage.getItem('bounds');
//         //                 var data = JSON.parse(store)
//         //                 if (!data) {
//         //                     data = {}
//         //                 }
//         //                 data['arrive'] = [result['y'], result['x']]
//         //                 localStorage.setItem('bounds', JSON.stringify(data));
//         //                 placerMarqueur(result, rec, false);
//         //             });
//         //     }
//         // });

//         // function onLocationError(e) {
//         //     alert(e.message);
//         // }

//         // if (navigator.geolocation) {
//         //     navigator.geolocation.getCurrentPosition(function(position) {
//         //         if (!isNaN(position.coords.latitude) && !isNaN(position.coords.longitude)) {
//         //             map.locate();

//         //             // add locate control
//         //             L.control.locate({
//         //                 strings: {
//         //                     title: "Ma position"
//         //                 }
//         //             }).addTo(map);
//         //         }
//         //     });
//         // }

//         // map.on('locationfound', onLocationFound);
//         // map.on('click', placerMarqueur);
//         // map.on('locationerror', onLocationError);

//         // $('#carte').on('shown.bs.tab', function(e) {
//         //     map.invalidateSize();
//         // });
//         sessionStorage.setItem('#carte', 'true');
//     });
// })
