odoo.define('evtc_taxi.fleet_vehicle_kanban', function (require) {
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');

    function renderUpdateVehicleButton() {
        if (this.$buttons) {
            var self = this;
            var lead_type = self.initialState.getContext()['default_type'];
            this.$buttons.on('click', '.o_button_update_vehicle', function () {
                return rpc.query({
                    model: 'fleet.vehicle',
                    method: 'update_vehicle_state_from_mo'
                }).then(function (res) {
                    const searchBox = document.querySelector('.o_searchview_input'); // Find the search box element
                    if (searchBox) { // Check if it exists
                        searchBox.addEventListener('keydown', function (event) { // Add event listener for keydown
                            if (event.key === 'Enter') { // Check if Enter key was pressed
                                event.preventDefault(); // Prevent default action of submitting form
                                searchBox.blur(); // Remove focus from search box to hide keyboard on mobile devices
                            }
                        });
                        searchBox.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' })); // Simulate Enter key press
                    }
                })
            });
        }
    }

    var UpdateVehicleStateKanbanController = KanbanController.extend({
        willStart: function () {
            this.buttons_template = 'evtc_taxi.update_vehicle_button';
            return Promise.all([this._super.apply(this, arguments)]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderUpdateVehicleButton.apply(this, arguments);
        }
    });

    var UpdateVehicleStateKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: UpdateVehicleStateKanbanController,
        }),
    });

    viewRegistry.add('update_vehicle_state_kanban', UpdateVehicleStateKanbanView);
});
