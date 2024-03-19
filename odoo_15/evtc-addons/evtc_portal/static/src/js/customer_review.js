odoo.define('evtc_portal.customer_review', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    window.starsValue = '0';

    publicWidget.registry.customerReview = publicWidget.Widget.extend({
        selector: "#customerReview",
        events: {
            'click button.oeSubmit': '_onSubmit_review',
            'click span.oe_img_select': '_onClickStars',
        },

        start: function () {
            this._super.apply(this, arguments)
            this.starsValue = '0';
        },

        _onSubmit_review: async function () {
            const leadIdentifier = $(this.el).find('input#crm_identifier')[0].value
            const parameter = {
                crm_id: leadIdentifier, review_value: window.starsValue
            }
            if (window.starsValue !== 0 || window.starsValue !== '0'){
                await this._rpc({
                    route: "/web/customer/review",
                    params: parameter
                }).then(xValue => {
                    if (xValue) {
                        const $element = $(this.el).find('div#custom-review-info')
                        $element.empty()
                        const htmlForm = `
                      <div class="d-flex rating-flex mx-auto mb16 mt-2">
                        <h3>Merci pour votre réponse</h3>
                      </div>
                    `
                        $element.append(htmlForm)
                    }
                })
            }
        },
        _onClickStars: function (events) {
            const FullStars = '<img class="d-block" src="/evtc_portal/static/src/img/ic_star.svg" ' +
                'width="48" height="48"/>';
            const BorderStars = '<img class="d-block" src="/evtc_portal/static/src/img/ic_star_border.svg" ' +
                'width="48" height="48"/>';
            const stars = events.currentTarget.attributes.value
            window.starsValue = stars.value
            const starsValueInt = parseInt(stars.value)
            const rating = $(this.el).find('#rating-step')
            rating.empty()
            for (let i = 1; i <= 5; i++) {
                const isFull = i <= starsValueInt ? FullStars : BorderStars
                const spanValue = `
                        <span value="` + i.toString() + `" style="cursor: pointer;" class="oe_img_select">
                            `+ isFull +`
                         </span>
                    `
                rating.append(spanValue)
            }
        }
    })
})
