odoo.define('vtc_area_destination.to_edit', function(require) {
    'use strict';

    const vtcMap = require('evtc_front.reservations')

    vtcMap.evtcArkeupMap.include({
        events: _.extend({}, vtcMap.evtcArkeupMap.prototype.events, {
            'click .to-modify': '_registerModification',
            'click .delivery_address_modify': '_modifyDestination',
        }),

        start: async function() {
            await this._super.apply(this, arguments)
        },

        _registerModification: async function(myAddress) {
            const address = myAddress.currentTarget.parentNode.attributes
            const addressId = this.render_selector_id(address.id.value)
            this._update_selector_value()
            const isPassed = this.check_validate_coordinate()

            const hasObject = {
                modification_id: 0,
                lat: null,
                lng: null,
                status: 'done',
                hasRegister: this._init_destination(true),
                isUpdate: addressId,
            }
            const latlng = this.$('#autocomplete-x1dCV')
            if (latlng[0] && latlng[0].classList.contains('next-content-suggestion')) {
                hasObject.lat = latlng.next()[0].value
                hasObject.lng = latlng.next().next()[0].value
            }

            if (isPassed) {

                const parameter = await this._get_params(hasObject)

                const destination = this.txContext.destination.filter(res => res.id === addressId)[0]

                if (parameter.status === 'done') {
                    this.active_details_id = addressId
                    this._show_destination(this._filter_li_data(addressId))
                    const selected_area = this.$('.destination-list-' + addressId)[0]
                    if (selected_area && (parameter._CurrentObject.details || parameter.Price)) {
                        const objectprice = parameter._CurrentObject.details ? parameter._CurrentObject.details : parameter.Price
                        $(selected_area).find('.address')[0].innerText = parameter._CurrentObject.name
                        $(selected_area).find('.waiting-minutes')[0].innerText = objectprice.name
                    }
                    this.initialized_coordinate_value()
                    this._toggle_add_destination()
                    try {
                        destination.marker.marker.setVisible(false)
                        destination.marker.label.close()
                        if (this.transientMarker.length > 0) {
                            this.transientMarker.forEach(transactor => {
                                transactor.marker.setVisible(false)
                                transactor.label.close()
                            })
                            this.transientMarker = []
                        }
                    } catch (e) {
                        console.error("an error occured: " + e)
                    }
                    await this._reorderSequence()
                    this._toggle_add_destination()
                }
            }
        },

        _modifyDestination: async function(events) {
            events.preventDefault()
            const object_selector_id = events.currentTarget.attributes.id.value
            if (object_selector_id) {
                const currentId = this.render_selector_id(object_selector_id)
                const selectedValue = this.txContext.destination.filter(res => res.id === currentId)
                const modification = this._filter_li_data(currentId)
                const existingModification = this.$(".oe-new-address-review")
                if (existingModification.length > 0) {
                    existingModification.attr('style', 'border: 1px solid red !important;')
                    return true
                } else if (selectedValue && selectedValue.length === 1) {
                    this._hide_onInsert()
                    selectedValue[0].marker.marker.setDraggable(false);
                    const hasObject = {
                        modification_id: currentId,
                        lat: null,
                        lng: null,
                        status: 'draft',
                        hasRegister: this._init_destination(false),
                        isUpdate: false,
                    }
                    const params = await this._get_params(hasObject)
                    if (params.status === 'edit') {
                        this._afterQweb(modification, this.txContext.selector.setXmlID, { setXml: params })
                        this._toggle_add_destination()
                        this._hide_destination(modification)
                        this.initialized_coordinate_value()
                        if (params._CurrentObject.details) {
                            this.active_details_id = params._CurrentObject.details.id
                        }
                        try {
                            const selected = this.$('#waiting_time')
                            const priceTime = this.$('.price-mod')
                            if (selected.length > 0 && params._CurrentObject.details) {
                                selected[0].value = (params._CurrentObject.details.id).toString() + ',' + (params._CurrentObject.details.price).toString()
                            }
                            if (priceTime.length > 0 && params._CurrentObject.details) {
                                priceTime[0].innerText = params._CurrentObject.details.price
                            }
                            this._disable_modification()
                        } catch (e) {
                            console.error("some module not load correctly: " + e)
                        }
                    }
                }
            }
        },
    })
})
