var switch_json;

$(function () {
    // Bind the swiperightHandler callback function to the swipe event on div.box
    $switchnav = $('#switchnav');
    $switchnav.on("swiperight", swiperightHandler);
    $switchnav.on("swipeleft", swipeleftHandler);

    // Callback function references the event target and adds the 'swiperight' class to it
    function swiperightHandler() {
        console.log(switch_json);

        if (switch_json.page_next === 'True') {

            window.location.href = switch_json.location_next;
        }
        else {
        }
    }

    // Callback function references the event target and adds the 'swiperight' class to it
    function swipeleftHandler() {

        if (switch_json.page_previous === 'True') {
            window.location.href = switch_json.location_previous;
        }
    }
});

