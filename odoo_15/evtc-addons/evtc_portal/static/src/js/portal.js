odoo.define('evtc_portal.contact', function (require) {

    if($("#showmore").length>0){
        $(document).on("click","#showmore",function(){
            $(".recently-wrap").toggleClass("show-item")

        })
    }
})
