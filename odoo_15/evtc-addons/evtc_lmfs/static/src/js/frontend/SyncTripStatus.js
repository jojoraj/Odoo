odoo.define('evtc_lmfs.SyncTripStatus', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.SyncTripStatus = publicWidget.Widget.extend({
        selector: '.lmfs-bloc',
        events: {
            'click .problem-btn': '_onClickProblemBtn',
        },

        start: function () {
            setInterval(this._checkStep.bind(this), 7000);
            return this._super.apply(this, arguments);
        },

        _checkStep: function () {
            let crm_id = document.querySelector('#evtc_aside').dataset.id
            rpc.query({
                model: 'crm.lead',
                method: 'progress_values',
                args: [crm_id]
            }).then(function (res) {
                let step = document.querySelector('.lmfs-bloc').dataset.step
                let text_step = document.getElementsByClassName("taxi-heading-2 text-center")[0].outerText
                if(String(res.step) === step && res.state_label!== text_step) location.reload()
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