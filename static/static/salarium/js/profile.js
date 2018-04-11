/**
 * Created by 11Linn on 12.11.16.
 */
var uploader = null;


function uploadThumbnail(){
    if (uploader === null) {
        uploader = new mediaUploader(undefined, function (data) {
            var image = $(data['image']);
            $('#user-thumbnail').css('background', "url('" + image.attr('src') + "') no-repeat center").css('background-size', 'cover');
            uploader.hide();

            var thumb_pk = image.attr('name');

            $.ajax({
                url: $('#item-thumbnail').data('save-thumbnail-url'),
                method: 'POST',
                data: {'image_pk': thumb_pk}
            }).done(function (result) {
                if(result['code'] == 200) {
                    $.growl({message: "Аватар обновлён", style: 'notice', title: 'Отлично!'});
                }
            });
        });
    }
    uploader.show();
}


$(document).ready(function() {
    $(window).load(function () {
        var galleryTop = new Swiper('.gallery-top', {
            nextButton: '.swiper-button-next',
            prevButton: '.swiper-button-prev',
            spaceBetween: 10
        });

        $('.open-gallery').on('click', function () {
            var pswpElement = document.querySelectorAll('.pswp')[0];

            var gallery_options = {
                index: $(this).data('index')
            };

            var images = [];

            $('.gallery-item').each(function () {
                var tempImage1 = new Image();
                tempImage1.src = $(this).data('src');
                tempImage1.onload = function () {
                    var W = tempImage1.width, H = tempImage1.height;
                    images.push({src: tempImage1.src, w: W, h: H});

                    if (images.length == $('.gallery-item').length) {
                        console.log(gallery_options);
                        var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, images, gallery_options);
                        gallery.init();
                    }
                };

            });
        });
    });
});