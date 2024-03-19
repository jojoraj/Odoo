odoo.define('evtc_portal.filter', function(require) {


    const publicWidget = require('web.public.widget');
    const widget = publicWidget.Widget
    const registry = publicWidget.registry
    const rpc = require('web.rpc')

    registry.filter = widget.extend({
        selector: "#content-courses",
        events: {
            'click #oe_filter_status': 'bySatus',
            'change input.changeEvent': 'byDate',
        },
        start: function() {
            var defs = [this._super.apply(this, arguments)];
            $('.loading').hide()
            return Promise.all(defs);
        },
        bySatus: async function() {
            await this._filter()
        },
        _render_Html: function(list, pager) {
            $('.container_list_course').empty()
            $('.pager_evtc').empty()
            $('.container_list_course').append(list)
            $('.pager_evtc').append(pager)
        },

        get_params: function() {
            return {
                'date_end': $("input[name='endDate']").val(),
                'date_begin': $("input[name='beginDate']").val(),
                'page': 1,
                'statusId': $('#oe_filter_status')[0].value
            }
        },

        _filter: async function() {
            $('.loading').show()
            await rpc.query({
                route: '/my/course/search',
                params: this.get_params()
            }).then(result => {
                let courseHtml = $(result.html_render).find('.container_list_course').html()
                let pager = $(result.html_render).find('.pager_evtc').html()
                this._render_Html(courseHtml, pager)
            }).catch(errors => {
                console.log(errors)
            });
            $('.loading').hide()
        },

        byDate: async function() {
            await this._filter()
        }
    })
    return {
        filters: registry.filter
    }
})
