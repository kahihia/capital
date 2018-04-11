/**
 * Created by 11Linn on 29.07.16.
 */

var disabled = false;
var currentSlide = 'slide1';

function checkIsSelect(element){
    if(!element.hasClass('count')) {
        element.find('.select-item').first().toggleClass('selected-product');
        $('.fp-controlArrow.fp-next').removeClass('hidden');
    }

    if(!$('.selected-product').length){
        $('.fp-controlArrow.fp-next').fadeOut();
    }else{
        $('.fp-controlArrow.fp-next').fadeIn();
    }
}

function moveSlide(slideAnchor, force){

    var slideNumber = slideAnchor.match(/\d+/)[0];

    if(!disabled || force === true){

        $('.bs-wizard-step').removeClass('active').addClass('disabled');

        for (var i = 0; i < slideNumber; i++) {
            $($('.bs-wizard-step')[i]).addClass('active').removeClass('disabled');
        }
        currentSlide = slideAnchor;
        $.fn.fullpage.moveTo(1, slideAnchor);

        $('#page-top').scrollTo($('#fullpageBasket').offset().top);
    }
}

function checkIsBasketEmpty(){
    if(!$('.order_item').length){
        $('#fullpageBasket').fadeOut();
        $('#basket-empty-state').fadeIn();
    }
}

function deleteOrderItemRequest(item, url){
    item = item.parent().parent().parent().parent().parent();
    $.ajax({
        url: url,
        crossDomain: true
    }).done(function (result) {
        if(result['code'] === 200) {
            $.growl({message: 'Товар успешно удален из корзины', style: 'notice', title: ''});
            item.animateCss('fadeOutLeft', function(){
                var index = parseInt(item.attr('id'));
                item.remove();

                var nexItem = $('#' + (index + 1));
                nexItem.css('margin-top', '215px');
                nexItem.animate({ 'marginTop': '0'}, 500);

                var counter = $('#basket_items_count');
                counter.html(parseInt(counter.html()) - 1);
                checkIsBasketEmpty();
            });
        }else if(result['code'] === 401){
            $.growl({message: 'Произошла ошибка', style: 'warning', title: ''});
        }
    });
}

function createTransaction(){
    var checkout_form = $('form#checkout-form'), orders_uuids = [];
    $('.select-item').each(function(){
        orders_uuids.push($(this).data('order-uuid').toString());
    });

    $.ajax({
        url: checkout_form.attr('action'),
        crossDomain: true,
        method: 'POST',
        data: JSON.stringify({form_data: checkout_form.serializeArray(), orders_uuids: orders_uuids}),
    }).done(function (result) {
        if (typeof (result) === 'string') {
            result = JSON.parse(result);
            var options = {
                type: 'inline',
                id: 'paymentForm',
                url: result['checkout']['redirect_url'],
                style: "",
                size: {height: 1100}
            };
            var pf = new BeGateway(options);
            pf.buildForm();
            moveSlide('slide3', true);
        }else {
            if (result['code'] === 200) {
                moveSlide('slide3', true);
                disabled = true;
                $('.fp-controlArrow.fp-prev').remove();
            } else if (result['code'] === 401) {
                $.growl({message: 'Произошла ошибка', style: 'warning', title: ''});
            }
        }
    });

}

function deleteOrder(item, url){
    bootbox.confirm({
        size: 'small',
        message: "<h4>Вы уверены, что хотите удалить этот предмет?</h4>",
        callback: function(result){ if(result){ deleteOrderItemRequest(item, url); } }
    });
}

$(window).resize(function(){
    $('.fp-controlArrow.fp-next').addClass('hidden');
});


function getStep() {
    var parts = window.location.href.split('/');
    var step = parts[parts.length - 1];
    if (step === ''){
        step = parts[parts.length - 2];
    }

    return step.indexOf('step=') !== -1 ? step.replace('step=', '') : undefined;

}

$(document).ready(function() {

    var step = getStep();
    if(step) {
          moveSlide(step, true);
    }

    $(window).load(function() {

        $('.order_item .manage-count').on('click', function(){
            var delta = $(this).hasClass('increase') ? 1 : -1,
                elem = $(this),
                max_count = $(this).parent().data('max-count');

            $.ajax({
                url: $(this).parent().data('change-count-url'),
                crossDomain: true,
                method: 'POST',
                data: {delta: delta}
            }).done(function (result) {
                if(result['code'] === 200) {
                    var newCount = parseInt(result['count']);
                    elem.parent().find('.orders-count').html(newCount);
                    if(newCount >= max_count){
                        elem.parent().find('.increase').addClass('hidden');
                        elem.parent().find('.decrease').removeClass('hidden');
                    }else if(newCount <= 1){
                        elem.parent().find('.increase').removeClass('hidden');
                        elem.parent().find('.decrease').addClass('hidden');
                    }else{
                        elem.parent().find('.increase').removeClass('hidden');
                        elem.parent().find('.decrease').removeClass('hidden');
                    }
                    $.growl({message: 'Количесвто товаров успешно изменено', style: 'notice', title: ''});

                    $('.total-price').html((result['total_price']).toFixed(2));
                    $('.discount-price').html((result['discount_price']).toFixed(2));
                    $('.total-discount').html((result['total_discount']).toFixed(2));

                    window.location.reload();
                }else if(result['code'] === 401){
                    $.growl({message: 'Произошла ошибка', style: 'warning', title: ''});
                }
            });
        });

        $('.count').on('click', function(event){
            event.stopPropagation();
        });

        $('.select-trigger').on('click', function(event){
            checkIsSelect($(this));
        });




        $('#fullpageBasket').fullpage({
            scrollOverflow: true,
            autoScrolling: false,
            loopHorizontal: false,
            slidesNavigation: false,
            verticalCentered: false,
            fitToSection: false,
            afterSlideLoad: function(){
                $('.section.active.fp-section.fp-completely').css('height','1000px');
            },
            onSlideLeave: function(anchorLink, index, slideIndex, direction, nextSlideIndex){
                if(nextSlideIndex === 1){
                    $('.fp-controlArrow.fp-next').fadeOut();
                }else if(nextSlideIndex === 0){
                    $('.fp-controlArrow.fp-next').fadeIn();
                }
            }
        });

        if($(document).height() <= $(window).height() ) {
            $('footer').css('bottom', '0');
        }

        $('#checkout-info').height($('#delivery-info').height());

        var galleryTop = new Swiper('.gallery-top', {
            nextButton: '.swiper-button-next',
            prevButton: '.swiper-button-prev',
            spaceBetween: 10
        });

        $('.open-gallery').on('click', function(){
            var pswpElement = document.querySelectorAll('.pswp')[0];

            var gallery_options = {
                index: $(this).data('index')
            };

            var images = [];

            $('.gallery-item').each(function(){
                var tempImage1 = new Image();
                tempImage1.src = $(this).data('src');
                tempImage1.onload = function() {
                    var W  = tempImage1.width, H = tempImage1.height;
                    images.push({src: tempImage1.src, w: W, h: H});

                    if(images.length == $('.gallery-item').length) {
                        console.log(gallery_options);
                        var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, images, gallery_options);
                        gallery.init();
                    }
                };

            });
        });


        $('.fp-controlArrow.fp-next').hide();

    });


});

