$(function () {
    var responsive = $(".responsive");
    responsive.css("display", "block");
    responsive.slick({
        dots: true,
        infinite: (responsive.attr("data-infinite").toLowerCase() === 'true'),
        speed: 300,
        arrows: false,
        slidesToShow: Number(responsive.attr("data-show")),
        slidesToScroll: Number(responsive.attr("data-show")),
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: Number(responsive.attr("data-show")),
                    slidesToScroll: Number(responsive.attr("data-show")),
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: Number(responsive.attr("data-show")) - 1,
                    slidesToScroll: Number(responsive.attr("data-show")) - 1
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: Number(responsive.attr("data-show")) - 2,
                    slidesToScroll: Number(responsive.attr("data-show")) - 2
                }
            }
            // You can unslick at a given breakpoint now by adding:
            // settings: "unslick"
            // instead of a settings object
        ]
    });
});