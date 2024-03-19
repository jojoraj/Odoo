odoo.define('evtc_location._events', function(require) {
    'use strict';
    const _OnExtendEvents = require('evtc_location.map');
    const $_events = _OnExtendEvents.evtcLocationMap;

    $_events.include({
        events: _.extend({}, $_events.prototype.events, {
            'click #evtc_recuperation_button_long': '_set_draggable_marker',
            'click #change_recuperation_appointment_long': '_set_modify_draggable_marker',
        }),
    });
})
