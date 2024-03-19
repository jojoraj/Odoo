odoo.define('lcas.arkeup._events', function(require) {
    'use strict';
    const _OnExtendEvents = require('evtc_front.reservations');
    const $_events = _OnExtendEvents.evtcArkeupMap;

    $_events.include({
        events: _.extend({}, $_events.prototype.events, {
            'click #evtc_recuperation_button': '_onClickRecuperationButton',
            'click #change_recuperation': '_set_modify_draggable_marker',
            'click #evtc_destination_button': '_set_draggable_marker_destination',
            'click #change_destination': '_set_modify_draggable_marker_destination',
        }),
    });
})
