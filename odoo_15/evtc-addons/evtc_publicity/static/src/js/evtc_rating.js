odoo.define('evtc_publicity.rating', function (require) {
    'use strict';
    const publicWidget = require('web.public.widget');
    const userSession = require('web.session')

    publicWidget.registry.rating = publicWidget.Widget.extend({
        selector: '#section_pub_vtc',
        events: {
            'click #save_rating': '_getRating',
            'click #number_click': '_getNumberClick',
        },
        _getRating: function () {
            let index = 0;
            let ratingValue = 0;
            for (let i = 0; i < document.getElementsByName('rating').length; i++) {
                if (document.getElementsByName('rating')[i].checked === true) {
                    ratingValue = document.getElementsByName('rating')[i].value;
                    index = i
                    break;
                }
            }
            let clientOpinion = $(this.el).find('#client-rate')[0].value
            this._rpc({
                route: '/register/rating',
                params: {
                    'rating': this._get_rating_params(ratingValue, clientOpinion),
                },
            }).then(() => {
                this._set_rating(index)
            })
        },
        _get_rating_params: function (rating, description) {
            return {
                'rate': rating,
                'Opinion': description
            }
        },
        _set_rating: function (j) {
            $('#modal_rating').modal('hide');
            document.getElementsByName('rating')[j].checked = false;
        },
        _getNumberClick: function (e) {
            let button_id = parseInt(e.target.dataset.id);
            this._rpc({
                route: '/count/click',
                params: {
                    'id': button_id,
                },
            }).then()
        }
    });
})
