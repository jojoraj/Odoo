odoo.define('evtc_taxi.taxi_features', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.TaxiFeatures = publicWidget.Widget.extend({
        selector: '.taxi-bloc',
        events: {
            'click .problem-btn': '_onClickProblemBtn',
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (true) {
                    self.taxiStepTimerInterval = setInterval(self._checkStep.bind(self), 30000);
                }
            });
        },
        _checkStep: function () {
            let self = this;
            let crm_id = document.querySelector('#evtc_aside').dataset.id
            rpc.query({
                model: 'crm.lead',
                method: 'progress_values',
                args: [crm_id]
            }).then(function (res) {
                let step = document.querySelector('.taxi-bloc').dataset.step
                if (String(res.step) !== step) {
                    location.reload()
                }
            })
        }
        ,
        _onClickProblemBtn: function (ev) {
            const element = document.querySelector('.o_livechat_button');
            const aside = document.querySelector('#evtc_aside');
            if (element) {
                element.click()
            } else {
                window.location.href = '/contactus?subject=' + encodeURIComponent('Course #' + aside.dataset.id);
            }
        }
    })
})
