odoo.define('mygeotabV1.MapView', function (require){
"use strict";

const MapModel = require('web_map.MapModel');
const MapController = require('web_map.MapController');
const WebMapView = require('web_map.MapView');
const MapRender = require('mygeotabV1.MapRenderer');
const AbstractView = require('web.AbstractView');
const viewRegistry = require('web.view_registry');

const MapView = WebMapView.extend({
    jsLibs: [
        '/web_map/static/lib/leaflet/leaflet.js',
        '/mygeotabV1/static/lib/leaflet/leaflet.rotatedMarker.js'
    ],
    config: _.extend({}, AbstractView.prototype.config, {
        Model: MapModel,
        Controller: MapController,
        Renderer: MapRender,
    }),
});
    viewRegistry.add('map', MapView);
    return MapView;
});
