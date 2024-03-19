odoo.define('autocomplet.log_per_session', function (require) {
    'use strict';

    var SessionRegister = require('evtc_location.map');
    var _session = SessionRegister.evtcLocationMap;

    _session.include({
        start: function () {
            this.OpportunityValidate = false;
            this.sessionRecuperation = 0;
            this.sessionDestination = 0;
            this._super.apply(this, arguments);
            this.sessionBooleanStore = this.check_current_token();
            this.sessionStoreToken = this.sessionToken;
            this.whosFields = '';
        },
        check_current_token: function () {
            var booleanStore = this.sessionStoreToken !== this.sessionToken
            return booleanStore
        },
        _click_li_option: function (li) {
            this.whosFields = 'recuperation';
            this._super.apply(this, arguments);
        },
        place_drag_destination: function (li) {
            this.whosFields = 'destination';
            this._super.apply(this, arguments);
        },
        get_active_input: function () {
            var bool_object = this.whosFields === 'recuperation'
            return bool_object
        },
        _get_new_session: function (input) {
            const self = this;
            if (self.get_active_input()) {
                self.sessionRecuperation += 1;
                console.info(self.sessionRecuperation)
            } else {
                self.sessionDestination += 1;
            }
            this.whosFields = '';
            this._super.apply(this, arguments);
        },
    })
})
