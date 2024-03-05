var iframe = $('.o_viewer_pdf')
iframe.on('load', function(){
    iframe.contents().find('body').attr('onselectstart','return false;')
    iframe.contents().find('.hiddenMediumView').hide();
    iframe.contents().find('.toolbarButton.openFile.hiddenLargeView').hide();
})