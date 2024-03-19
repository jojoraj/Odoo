odoo.define('myadress.evtc.portal', function (require) {
    'use strict';

    const _ajax = require('web.ajax')
    const myadress = require('myadress.evtc.map')
    const _TokenSession = myadress.saveModalAdress

    const myadressSession = _TokenSession.include({
        events: _.extend({}, _TokenSession.prototype.events, {
            'focusout #input_partner_street': 'myaccount_initialized_session',
            'click #btnSubmit': 'myaccount_user_log',
        }),
        start: function(){
            this.sessionToken = new google.maps.places.AutocompleteSessionToken();
            this.myadress = false;
            this.myaccount_service = 0;
            this._super.apply(this, arguments);
            this.options.sessionToken = this.sessionToken;
            window.addEventListener('beforeunload', () => {
                if (this.myaccount_service && !this.myadress) {
                    const data = {
                        'myaccount_service': this.myaccount_service,
                        'isValidate': this.myadress,
                    };
                    _ajax.jsonRpc('/session-log', 'call', data)
                }
            });
        },

        myaccount_initialized_session: function (e) {
            e.preventDefault();
            const $_recup_input = e.target.value
            const long = $_recup_input.length
            if (long && long > 3) {
                this.sessionToken = new google.maps.places.AutocompleteSessionToken();
                this.myaccount_service ++;
            }
        },

        myaccount_user_log: function () {
            this.myadress = true
            const partner = Boolean($('#partner_name').val())
            const data = {
                'myaccount_service': this.myaccount_service,
                'isValidate': this.myadress,
            };
            if (partner) {
                _ajax.jsonRpc('/session-log', 'call', data)
            }
        }
    });
    return myadressSession;
})
