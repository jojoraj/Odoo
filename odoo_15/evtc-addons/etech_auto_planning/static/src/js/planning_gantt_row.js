/** @odoo-module alias=etech_auto_planning.AutoPlanningGanttRow **/

const PlanningGanttRow = require('planning.PlanningGanttRow');

const AutoPlanningGanttRow = PlanningGanttRow.include({
    /*_getPopoverContext: function () {
        const data = this._super.apply(this, arguments);
        data.allocatedHoursFormatted = fieldUtils.format.float_time(data.allocated_hours);
        data.allocatedPercentageFormatted = fieldUtils.format.float(data.allocated_percentage);
        return data;
    },*/
});

export default AutoPlanningGanttRow;
