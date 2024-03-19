odoo.define('lcas.arkeup.token', function(require) {
    'use strict';

    var $_ajax = require('web.ajax');
    const SessionTokenImplement = require('evtc_front.reservations');
    const _Token = SessionTokenImplement.evtcArkeupMap;

    const sessionToken = _Token.include({
        events: _.extend({}, _Token.prototype.events, {
            'focusout #address_recuperation': '_initialized_recup_session',
            'focusout #address_destination': '_initialized_dest_session',
        }),
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            this.sessionToken = new google.maps.places.AutocompleteSessionToken();
            this.autocompleteSuggestion.sessionToken = this.sessionToken;
            this.OpportunityValidate = false;
            this.sessionRecuperation = 0;
            this.sessionDestination = 0;
            window.addEventListener('beforeunload', () => {
                if (this.sessionRecuperation || this.sessionDestination && !this.OpportunityValidate) {
                    const data = {
                        'recuperation': this.sessionRecuperation,
                        'destination': this.sessionDestination,
                        'isValidate': this.OpportunityValidate,
                    };
                    $_ajax.jsonRpc('/session-log', 'call', data)
                }
            });
            return Promise.all(defs);
        },
        _initialized_recup_session: function(e) {
            e.preventDefault();
            const $_recup_input = e.target.value
            const long = $_recup_input.length
            if (long && long > 3) {
                this.sessionToken = new google.maps.places.AutocompleteSessionToken();
                this.sessionRecuperation++;
            }
        },
        _initialized_dest_session: function(z) {
            z.preventDefault();
            const $_dest_input = z.target.value
            const long = $_dest_input.length
            if (long && long > 3) {
                this.sessionToken = new google.maps.places.AutocompleteSessionToken();
                this.sessionDestination++;
            }
        },
        record_user_log: function() {
            this.OpportunityValidate = true
            const data = {
                'recuperation': this.sessionRecuperation,
                'destination': this.sessionDestination,
                'isValidate': this.OpportunityValidate,
            };
            $_ajax.jsonRpc('/session-log', 'call', data)
        }
    });
    return sessionToken;
})
