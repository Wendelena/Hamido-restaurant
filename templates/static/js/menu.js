$(function () {

    $('a[href^="#"]').on('click', function(event) {

        var target = $( $(this).attr('href') );

        if( target.length ) {
            event.preventDefault();
            $('html, body').animate({scrollTop: (target.offset().top - 90)}, "fast", "swing");
        }

    });

    var slideIndex = 0;
    var capacity = 3;

    $(function carousel() {
        slideIndex ++;
        if (slideIndex >= capacity) {
            slideIndex = 0;
        }
        $(".carousel").each(function () {
            var x = $(this);
            x.fadeOut(1000, function () {
                x.css('background-image', 'url(static/img/menuphoto/' + x.attr('id') + '-' + (slideIndex + 1) + '.jpg)');
                x.fadeIn(1000, false);
            });
        });

        setTimeout(carousel, 5000); // Change image regularly
    });

});