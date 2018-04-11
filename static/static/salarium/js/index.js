/**
 * Created by 11Linn on 29.07.16.
 */
$(document).ready(function () {

    $(window).load(function () {
        $('.posts-container').justifiedGallery({
            margins: 5,
            rowHeight: ($(window).height() - 350) / 3,
            lastRow: 'nojustify'
        });

        $('.justified-gallery>a, .justified-gallery>div').each(function () {
            $(this).css('display', 'inline-block !important');
            $(this).css('position', 'initial !important');
        });

        $('#fullpage').fullpage({
            navigation: true,
            scrollOverflow: true,
            afterRender: function () {
                $('#fullpage').css('opacity', '1');
                $('.preloader').remove();
            }
        });



    });


});

