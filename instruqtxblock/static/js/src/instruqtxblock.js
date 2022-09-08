/* Javascript for InstruqtXBlock. */
function InstruqtXBlock(runtime, element) {

  
    var handlerUrl = runtime.handlerUrl(element, 'completion_handler');

    function completeTrack(data) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data)
        });
    };

    window.addEventListener(
        "message",
        (event) => {
            if (event.origin !== "https://play.instruqt.com") {
                return;
            }

            console.log(
                "Received event:",
                event.data.event,
                "with params:",
                event.data.params
            );

            if (event.data.event === "track.completed") {
                completeTrack(event.data);
            }
        },
        false
    ); 
}
