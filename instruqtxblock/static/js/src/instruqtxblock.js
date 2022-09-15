/* Javascript for InstruqtXBlock. */
function InstruqtXBlock(runtime, element) {

  
    var handlerUrl = runtime.handlerUrl(element, 'completion_handler');


    function openFullscreen(elem) {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { /* Safari */
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { /* IE11 */
            elem.msRequestFullscreen();
        }
    }
  
    function completeTrack(data) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data)
        });
    };

    $(function ($) {  
        
        $('.btn-fullscreen').click(function(event) {
            event.preventDefault();
            var el = document.querySelector(".instruqtxblock_block iframe")
            openFullscreen(el);
        });      
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

                if (event.data.event === "track.completed" || event.data.event === "track.challenge_completed") {
                    completeTrack(event.data);
                }
            },
            false
        ); 
    });
}
