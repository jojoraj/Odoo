odoo.define('invoice.action_button', function (require) {
    'use strict';
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var _t = core._t;

    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
           if (this.$buttons) {
             this.$buttons.find('.oe_action_button_lead_leads').click(this.proxy('action_leads_def'));
             this.$buttons.find('.oe_action_button_lead_opportunities').click(this.proxy('action_opportunities_def'));
             this.$buttons.find('.oe_action_button_tender').click(this.proxy('action_tender_def'));
           }
        },

        action_leads_def: function () {
            var self = this;
            rpc.query({
                model: "crm.lead",
                method: "open_import_leads_wizard",
                args: [self.id],
            }).then(function (e) {
                self.do_action({
                    name: _t(self.display_name),
                    type: 'ir.actions.act_window',
                    res_model: 'ir.model.import.template',
                    views: e.views,
                    res_id: e.res_id,
                    view_mode: 'form',
                    target: 'new',
                    context: self.initialState.context
                });
                window.location
            });
        },
        action_opportunities_def: function () {
            var self = this;
            rpc.query({
                model: "crm.lead",
                method: "open_import_opportunities_wizard",
                args: [self.id],
            }).then(function (e) {
                self.do_action({
                    name: _t(self.display_name),
                    type: 'ir.actions.act_window',
                    res_model: 'ir.model.import.template',
                    views: e.views,
                    res_id: e.res_id,
                    view_mode: 'form',
                    target: 'new',
                    context: self.initialState.context
                });
                window.location
            });
        },

        action_tender_def: function () {
            var self = this;
            rpc.query({
                model: "crm.lead",
                method: "open_import_tender_wizard",
                args: [self.id],
            }).then(function (e) {
                self.do_action({
                    name: _t(self.display_name),
                    type: 'ir.actions.act_window',
                    res_model: 'ir.model.import.template',
                    views: e.views,
                    res_id: e.res_id,
                    view_mode: 'form',
                    target: 'new',
                    context: self.initialState.context
                });
                window.location
            });
        },
    })
    
})