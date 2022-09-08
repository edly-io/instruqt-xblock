// function InstruqtStudioXBlock(runtime, element, args) {
   
    // var handlerUrl = runtime.handlerUrl(element, 'studio_submit');


    // $(element).find('.save-button').bind('click', function () {
    //     var form_data = new FormData();
    //     var display_name = $(element).find('input[name=xb_display_name]').val();
    //     var track_embed_code = $(element).find('#xb_track_embed_code').val();
    //     var track_iframe_width = $(element).find('#xb_track_iframe_width').val();
    //     var track_iframe_height = $(element).find('#xb_track_iframe_height').val();        

    //     form_data.append('track_embed_code', track_embed_code);
    //     form_data.append('display_name', display_name);
    //     form_data.append('track_iframe_width', track_iframe_width);
    //     form_data.append('track_iframe_height', track_iframe_height);


    //     if ('notify' in runtime) { //xblock workbench runtime does not have `notify` method
    //         runtime.notify('save', { state: 'start' });
    //     }        

    //     $.ajax({
    //         url: handlerUrl,
    //         dataType: 'text',
    //         cache: false,
    //         contentType: false,
    //         processData: false,
    //         data: form_data,
    //         type: "POST",
    //         success: function (response) {
    //             if ('notify' in runtime) { //xblock workbench runtime does not have `notify` method
    //                 runtime.notify('save', { state: 'end' });
    //             }
    //         }
    //     });

    // });

    // $(element).find('.cancel-button').bind('click', function () {
    //     if ('notify' in runtime) { //xblock workbench runtime does not have `notify` method
    //         runtime.notify('cancel', {});
    //     }
    // });

// }

