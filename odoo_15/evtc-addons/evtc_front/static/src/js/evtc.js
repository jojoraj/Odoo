odoo.define('evtc_front.evtc', function(require) {
    function scrollAside(selector, element, delay) {
        var headerHeight = ($(".oe_connected_user").length > 0) ? 120 : 60
        selector.animate({
            scrollTop: element.offset().top - headerHeight
        }, delay);
    }
    $(document).ready(function() {
        if ($('.signup').length > 0) {
            $('body').addClass("signup");
        }

        /* Country selekta*/

        function format(state) {
            var originalOption = state.element;

            return "<div class='d-flex align-items-center'>" +
                "<i class='d-inline-block mr-2 flag flag-" + state.id.toLowerCase() + " '></i>" +
                "<span class='d-inline-block mr-2'>" + state.text.split('$')[0] + "</span>" +
                "<span class='d-inline-block text-phone' style='font-size:14px'>+(" + $(originalOption).data('phone') + ")</span>" +
                "</div>";
        }

        function formatSelection(state) {

            return "<div class='d-flex align-items-center'>" +
                "<i class='d-inline-block mr-2 flag flag-" + state.id.toLowerCase() + " '></i>" +
                "</div>";
        }
        $(".country_selekta").select2({
            searchInputPlaceholder: "Chercher par pays",
            formatResult: format,
            formatSelection: formatSelection,
            dropdownParent: $(".form-group")
        });

        $('.evtc-form').show();
        /* End*/
        if ($("div#wrap").hasClass("reservation_evtc")) {
            $("footer#bottom").addClass("d-none");
        }

        // $('.remove_val_button').click(function() {
        //     $(this).next('.remove_val_input').val('');
        // });

        if ($('.country-flag-input').length > 0) {
            const observer = new MutationObserver(list => {
                const evt = new CustomEvent('drop-open', { detail: list });
                document.body.dispatchEvent(evt)
            });
            observer.observe(document.querySelector('div.country_selekta'), { attributes: true, childList: true, subtree: true });
            document.body.addEventListener('drop-open', () => {
                if ($('div.country_selekta').hasClass('select2-dropdown-open')) {
                    $('#select2-drop-mask').append('<h2 class="drop-title d-md-none">Pays du numéro de téléphone</h2>')
                } else {
                    $('#select2-drop-mask').find('h2').remove()
                }
            });
        }

    })

    /**
    Debut **/
    function onKeyboardOnOff(isOpen) {
        // Write down your handling code
        if (isOpen) {
            // Keyboard is open
            $('#evtc_aside').addClass('open');
        } else {
            // Keyboard is closed
            $('#evtc_aside').removeClass('open');
        }
    }

    var originalPotion = false;
    $(document).ready(function() {
        if (originalPotion === false) originalPotion = $(window).width() + $(window).height();
    });

    /**
     * Determine the mobile operating system.
     * This function returns one of 'iOS', 'Android', 'Windows Phone', or 'unknown'.
     *
     * @returns {String}
     */
    function getMobileOperatingSystem() {
        var userAgent = navigator.userAgent || navigator.vendor || window.opera;

        // Windows Phone must come first because its UA also contains "Android"
        if (/windows phone/i.test(userAgent)) {
            return "winphone";
        }

        if (/android/i.test(userAgent)) {
            return "android";
        }

        // IOS detection from: http://stackoverflow.com/a/9039885/177710
        if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
            return "ios";
        }

        return "";
    }

    function applyAfterResize() {

        if (getMobileOperatingSystem() !== 'ios') {
            if (originalPotion !== false) {
                var wasWithKeyboard = $('body').hasClass('view-withKeyboard');
                var nowWithKeyboard = false;

                var diff = Math.abs(originalPotion - ($(window).width() + $(window).height()));
                if (diff > 100) nowWithKeyboard = true;

                $('body').toggleClass('view-withKeyboard', nowWithKeyboard);
                if (wasWithKeyboard !== nowWithKeyboard) {
                    onKeyboardOnOff(nowWithKeyboard);
                }
            }
        }
    }



    $(window).on('resize orientationchange', function() {
        applyAfterResize();
    });

    /**
    Fin **/

})
