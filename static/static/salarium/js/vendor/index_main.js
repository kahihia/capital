function changeMainSlide(elem) {
    var activeSlide = $('.selected-slide');

    hideSlide(activeSlide, showNewImage, {src: elem.data('img'), href: elem.data('href')});
    showSlide(elem);
}

function showNewImage(newImgData) {
    let elem = $('#slide-image-container');
    elem.css('background-image', 'url(' + newImgData.src + ')');
    elem.data('href', newImgData.href);
    elem.animateCss('fadeInRight', function () {});
}

function showSlide(slide) {
    slide.addClass('selected-slide');
    slide.find('.slide-title').addClass('hactive');
    slide.find('.linetitle, .subtitle').slideDown();
}

function hideSlide(slide, callback, callback_args) {
    slide.removeClass('selected-slide');
    slide.find('.slide-title').removeClass('hactive');
    slide.find('.linetitle, .subtitle').slideUp("normal", function () {

    });

    $('#slide-image-container').animateCss('fadeOutRight', function () {
        callback(callback_args);
    });
}

$(document).ready(function () {

    $(window).load(function () {

        var slidesCount = $('#slides-count').data('count');

        $('#slide-image-container').animateCss('fadeInRight', function () {
            $('#slide-image-container').show();
        });

        $('#slide-image-container').on('click', function(){
            window.open($(this).data('href'), '_blank');
        });

        $('#slider-scroll-down').on('click', function () {
            $('body').scrollTo($('#main-container').offset().top - $('.navbar-scroll-fixed ').height());
        });

        // progressbar.js@1.0.0 version is used
// Docs: http://progressbarjs.readthedocs.org/en/1.0.0/

        if (typeof(circle) !== "undefined") {
            var bar = new ProgressBar.Circle(circle, {
                color: '#aaa',
                // This has to be the same size as the maximum width to
                // prevent clipping
                strokeWidth: 3,
                trailWidth: 1,
                easing: 'easeInOut',
                duration: 4400,
                text: {
                    autoStyleContainer: false
                },
                from: {color: '#aaa', width: 1},
                to: {color: '#333', width: 3},
                // Set default step function for all animate calls
                step: function (state, circle) {
                    circle.path.setAttribute('stroke', state.color);
                    circle.path.setAttribute('stroke-width', state.width);

                    var value = Math.round(circle.value() * 1);
                    if (value === 1) {
                        circle.setText('1/' + slidesCount);
                    } else {
                        circle.setText('0/' + slidesCount);
                    }
                }
            });

            bar.text.style.fontFamily = '"Raleway", Book';
            bar.text.style.fontSize = '13px';

            bar.animate(1.0);  // Number from 0.0 to 1.0
        }
    });
});