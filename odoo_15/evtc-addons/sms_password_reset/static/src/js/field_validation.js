odoo.define('sms_password_reset.field_validation', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var validationCode = require('signup_validation_code.signup_confirmation')
    const signup_confirmation = validationCode.signup_confirmation

    signup_confirmation.include({
        _newClick_Validation: function() {
            const self = this;
            const alert_p = '<p id="alert_code" class="alert alert-danger-new" role="alert">'
            const alert_code_input = '<p id="alert_code_input" class="alert-code-input alert alert-danger-new" role="alert">'
            const parent_element = $('#code-input');
            const code = $('#code').val();
            self._delete_alert_code('#alert_code');
            self._delete_alert_code('#alert_code_input');
            if (!code) {
                $(alert_code_input + ' Code required<p>').insertAfter(parent_element);
            }
            if (code) {
                ajax.jsonRpc('/json/check/code', 'call', {
                    'default_sms': 'default_sms',
                    'code': $('#code').val(),
                    'token': $('#token').val(),
                }).then(function (result){
                    self._delete_alert_code('#alert_code');
                    if (result.status === 200) {
                       window.location.assign(result.url);
                    } else {
                        $(alert_p + result.error + '<p>').insertAfter(parent_element);
                    }
                })
            }
        },
        _OnClickConfirmValidationCode: function (event) {
            try {
                const default_sms = $('#default_sms').val()
                if (default_sms && default_sms === 'reset_password') {
                    this._newClick_Validation()
                } else {
                    this._super.apply(this, arguments);
                }
            } catch (e) {
                console.error(e)
            }

        },
    })
})
