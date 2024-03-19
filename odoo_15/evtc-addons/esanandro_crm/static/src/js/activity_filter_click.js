/** @odoo-module **/

import ActivityMenu from '@mail/js/systray/systray_activity_menu';

ActivityMenu.include({
    /**
     * @private
     * @override
     */
    _onActivityFilterClick: function (event) {
        let data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
        if (data.res_model === "crm.record.lead") {
            return this._rpc({
                model: 'res.users',
                method: 'get_domain',
                args: [[]],
                kwargs: {filter: data.filter},
            }).then(z =>
                this.do_action({
                    type: 'ir.actions.act_window',
                    name: 'Pipeline',
                    views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
                    view_mode: 'kanban',
                    res_model: 'crm.lead',
                    domain: z[0],
                }, {
                    clear_breadcrumbs: true,
                })
            );
        } else {
            this._super.apply(this, arguments);
        }
    },
});
