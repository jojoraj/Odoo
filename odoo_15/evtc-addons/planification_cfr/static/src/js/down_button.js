odoo.define('planification_cfr.down_button', function (require) {
    "use strict";

    const PlanningGanttController = require('planning.PlanningGanttController');

    var NewPlanningGanttController = PlanningGanttController.include({
        events: Object.assign({}, PlanningGanttController.prototype.events, {
            'click .o_down_plan_xlsx': '_download_xlsx_cfr',
        }),
        buttonTemplateName: 'DownGanttView.buttons',
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _download_xlsx_cfr: function (ev) {
            ev.preventDefault();
            var context = {};
            var state = this.model.get();
            context[state.dateStartField] = this.model.convertToServerTime(state.focusDate.clone().startOf(state.scale));
            context[state.dateStopField] = this.model.convertToServerTime(state.focusDate.clone().endOf(state.scale));
            this._rpc({
                model: 'request.result.list',
                method: 'download_last_file',
                args: [context]
            }).then((result) => {
                if (result) {
                    window.location = `/web/content/${result}?download=true`;
                } else{
                    alert("Nous n'avons pas de fichier de planification correspondant à cette période.")
                }

            })
        },

    });
    return NewPlanningGanttController;
});
