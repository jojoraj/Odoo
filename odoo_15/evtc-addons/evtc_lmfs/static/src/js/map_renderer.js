odoo.define('lmfs_vtc.MapRenderer', function (require) {
    "use strict"

    const WebMapRenderer = require('web_map.MapRenderer');

    const mapTileAttribution = `
        © <a href="https://www.mapbox.com/about/maps/">Mapbox</a>
        © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>
        <strong>
            <a href="https://www.mapbox.com/map-feedback/" target="_blank">
                Improve this map
            </a>
        </strong>`;

    // Const ExtendsMapRenderer = MapRenderer =>
    class MapRender extends WebMapRenderer {
        async willStart() {
            // Super.willStart(...arguments);
            const p = { method: 'GET' };
            // If (window.location.hash.indexOf('fleet.vehicle') > 1) {
            if (this.props.arch.attrs.res_partner === 'driver_id') {
                [this._carTopviewSVG,this._carTopLmfs,this._carTopGeotab] = await Promise.all([
                    this.env.services.httpRequest('evtc_lmfs/static/img/car_topview.svg', p, 'text'),
                    this.env.services.httpRequest('evtc_lmfs/static/img/Phone2.svg', p, 'text'),
                    this.env.services.httpRequest('evtc_lmfs/static/img/router2.svg', p, 'text'),
                ]);
            } else {
                [this._pinCircleSVG, this._pinNoCircleSVG] = await Promise.all([
                    this.env.services.httpRequest('web_map/static/img/pin-circle.svg', p, 'text'),
                    this.env.services.httpRequest('web_map/static/img/pin-no-circle.svg', p, 'text'),
                ]);
            }

            // }
            return super.willStart(...arguments);

        }

        async updateLatLng() {
            await this.env.services.rpc({
                model: "fleet.vehicle",
                method: "get_latlong",
                args: [],
            });
        };

        async getdevicestatusinfo() {
            var devicestatusinfo;
            await this.env.services.rpc({
                model: "fleet.vehicle",
                method: "getdevicestatusinfo",
                args: [],
            }).then(function (result) {
                devicestatusinfo = result
            })
            return devicestatusinfo;
        };

        mounted() {
            var self = this;
            super.mounted(...arguments);
            setTimeout(() => {
                const repositionning = setInterval(async () => {
                    if (window.location.hash.indexOf('fleet.vehicle&view_type=map') > 1) {
                        const params = { model: "fleet.vehicle", method: "getdevicestatusinfo" }
                        await this.env.services.rpc(params)
                            .then(async (devicestatusinfo) => {
                                var device_list = devicestatusinfo.map( a => a.immatriculeID);
                                for (var marker of self.markers) {
                                    if (device_list.includes(marker.options.license_plate)) {                            
                                        var index_device_coordinate = devicestatusinfo.findIndex(x => x.immatriculeID === marker.options.license_plate);
                                        var latitude = devicestatusinfo[index_device_coordinate].latitude;
                                        var longitude = devicestatusinfo[index_device_coordinate].longitude;
                                        var heading = devicestatusinfo[index_device_coordinate].bearing;
                                        marker.setLatLng(L.latLng(latitude, longitude))
                                    
                                        marker.options.icon.rotation = heading - 90
                                    }
                                }
                            }, error=>{
                                console.log(error)
                            })
                            
                    } else {
                        clearInterval(repositionning);
                    }
                }
                    , 2000)
            }, 5000); // 1000 milliseconds delay
        }

        /**
         * If there's located records, adds the corresponding marker on the map.
         * Binds events to the created markers.
         *
         * @private
         */
        _addMarkers() {
            // If (window.location.hash.indexOf('fleet.vehicle') > 1) {
            this._removeMarkers();
            const markersInfo = {};
            let records = this.props.records;
            if (this.props.groupBy) {
                records = Object.entries(this.props.recordGroups)
                    .filter(([key]) => !this.state.closedGroupIds.includes(key))
                    .flatMap(([, value]) => value.records);
            };
            this.updateLatLng();
            // }

            for (const record of records) {
                const partner = record.partner;
                if (partner && partner.partner_latitude && partner.partner_longitude) {
                    const key = `${partner.partner_latitude}-${partner.partner_longitude}`;
                    if (key in markersInfo) {
                        markersInfo[key].record = record;
                        markersInfo[key].ids.push(record.id);
                    } else {
                        markersInfo[key] = { record: record, ids: [record.id] };
                    }
                }
            }
            var test = this._carTopviewSVG
            for (const markerInfo of Object.values(markersInfo)) {
                var pinSVG;
                // if(markerInfo.record.geolocalization_type === 'lmfs') pinSVG = this._carTopLmfs
                // if(markerInfo.record.geolocalization_type === 'geotab') pinSVG = this._carTopGeotab
                //if(markerInfo.record.geolocalization_type === false) 
                // pinSVG = this._carTopviewSVG 
                const params = {
                    count: markerInfo.ids.length,
                    isMulti: markerInfo.ids.length > 1,
                    number: this.props.records.indexOf(markerInfo.record) + 1,
                    numbering: this.props.numbering,
                    pinSVG: test,
                };
                if (this.props.groupBy) {
                    const group = Object.entries(this.props.recordGroups)
                        .find(([, value]) => value.records.includes(markerInfo.record));
                    params.color = this._getGroupColor(group[0]);
                }
                // Icon creation
                var iconInfo = {
                    className: 'o_map_marker',
                    html: this.env.qweb.renderToString('web_map.marker', params),
                }
                // Attach marker with icon and popup
                const color = markerInfo.record.marker_color
                if (color !== undefined) {
                    var html_change = iconInfo.html.replace("<svg", "<svg fill= '" + color + "'");
                    iconInfo = {
                        className: 'o_map_marker',
                        html: html_change,
                    }
                }
                const marker = L.marker([
                    markerInfo.record.partner.partner_latitude,
                    markerInfo.record.partner.partner_longitude
                ], { icon: L.divIcon(iconInfo), license_plate: markerInfo.record.license_plate });
                marker.addTo(this.leafletMap);
                marker.on('click', () => {
                    this._createMarkerPopup(markerInfo, self = this);
                });
                this.markers.push(marker);

            }
            // }
            //     else{
            //         super._addMarkers()
            //     }
        }

        /**
         * Create a popup for the specified marker.
         *
         * @private
         * @param {Object} markerInfo
         */
        async _createMarkerPopup(markerInfo) {
            const popupFields = this._getMarkerPopupFields(markerInfo);
            var popup;
            var self = this;
            await this.env.services.rpc({
                model: 'fleet.vehicle',
                method: 'get_partner_coordinate',
                args: [markerInfo.record.partner.id],
            }).then(function (result) {
                // Const partner = markerInfo.record.partner;
                const partner = result;
                const popupHtml = self.env.qweb.renderToString('web_map.markerPopup', {
                    fields: popupFields,
                    hasFormView: self.props.hasFormView,
                    url: `https://www.google.com/maps/dir/?api=1&destination=${partner.partner_latitude},${partner.partner_longitude}`,
                });

                popup = L.popup({ offset: [0, -30] })
                    .setLatLng([partner.partner_latitude, partner.partner_longitude])
                    .setContent(popupHtml)
                    .openOn(self.leafletMap);

                const openBtn = popup.getElement().querySelector('button.o_open');
                if (openBtn) {
                    openBtn.onclick = () => {
                        self.trigger('open_clicked', { ids: markerInfo.ids });
                    };
                }

            })
            return popup;

        }

        // ----------------------------------------------------------------------
        // Handlers
        // ----------------------------------------------------------------------

        /**
         * Center the map on a certain pin and open the popup linked to it.
         *
         * @private
         * @param {Object} record
         */
        async _centerAndOpenPin(record) {
            const popup = await this._createMarkerPopup({
                record: record,
                ids: [record.id],
            });
            const px = this.leafletMap.project([record.partner.partner_latitude, record.partner.partner_longitude]);
            const popupHeight = popup.getElement().offsetHeight;
            px.y -= popupHeight / 2;
            const latlng = this.leafletMap.unproject(px);
            this.leafletMap.panTo(latlng, { animate: true });
        }

        /**
         * Get the fields' name and value to display in the popup.
         *
         * @private
         * @param {Object} markerInfo
         * @returns {Object} value contains the value of the field and string
         *                   contains the value of the xml's string attribute
         */
        _getMarkerPopupFields(markerInfo) {
            const record = markerInfo.record;
            const fieldsView = [];
            // Only display address in multi coordinates marker popup
            if (markerInfo.ids.length > 1) {
                if (!this.props.arch.attrs.res_partner === 'driver_id') {
                    if (!this.props.hideAddress) {
                        fieldsView.push({
                            value: record.partner.contact_address_complete,
                            string: this.env._t("Address"),
                        });
                    }
                }

                return fieldsView;
            }
            if (!this.props.hideName) {
                fieldsView.push({
                    value: record.display_name,
                    string: this.env._t("Name"),
                });
            }
            for (const field of this.props.fieldNamesMarkerPopup) {
                if (!field.fieldName === "license_plate" || !field.fieldName === "marker_color") {
                    if (record[field.fieldName]) {
                        const fieldName = record[field.fieldName] instanceof Array ?
                            record[field.fieldName][1] :
                            record[field.fieldName];
                        fieldsView.push({
                            value: fieldName,
                            string: field.string,
                        });
                    }
                }
            }


            return fieldsView;
        }

    }

    return MapRender;
})
