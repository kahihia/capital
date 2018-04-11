/**
 * Created by linnnai on 5.1.16.
 */
var library = null, slideoutOpened = false, slideoutClosed = true;



$(window).ready(function () {

    $(document).ready(function () {

        $.extend($.scrollTo.defaults, {
            axis: 'y',
            duration: 500
        });

        $(".slider").slider({
            tooltip_split: true
        });

        if ($('div.modal-backdrop-container').height() <= $(window).height()) {
            $('div.modal-backdrop-container').css('min-height', ($(window).height() - 137).toString() + 'px');
        }

        if ($('div.heading-background').height() <= $(window).height()) {
            $('div.heading-background').css('min-height', ($(window).height()).toString() + 'px');
        }

        $('input[type="checkbox"]').change(function () {
            var value = $(this).is(":checked");
            var label = $("label[for='" + $(this).attr('id') + "']");
            value ? label.attr('checked', true) : label.removeAttr('checked');
        });

    });

    NProgress.start();

    $('.selectpicker').selectpicker({
        style: 'btn-default',
        size: 4
    });

    if ($('#panel').length > 0) {
        $('footer').hide();

        $('nav#menu').css('margin-left', '-256px');

        var slideout = new Slideout({
            'panel': document.getElementById('panel'),
            'menu': document.getElementById('menu'),
            'padding': 260,
            'tolerance': 70
        });

        $('main#panel').on('click', function () {
            if (slideout.isOpen() && slideoutOpened) {
                slideout.toggle();
                $('.toggle-button').find('i').removeClass('glyphicon-arrow-left').addClass('glyphicon-arrow-right');
            }
        });

        slideout.on('beforeopen', function () {
            $('nav#menu').animate({marginLeft: '+=256px'}, 300);
            // $('.fixed').addClass('fixed-open');
        });

        slideout.on('beforeclose', function () {
            $('nav#menu').animate({marginLeft: '-=256px'}, 300);
        });

        slideout.on('open', function () {
            slideoutOpened = true;
            slideoutClosed = false;
        });

        slideout.on('close', function () {
            slideoutOpened = false;
            slideoutClosed = true;
        });

        slideout.on('beforeclose', function () {
            $('.fixed').removeClass('fixed-open');
        });
    }

    $('.toggle-button').on('click', function () {
        slideout.toggle();
        if (slideout.isOpen()) {
            $(this).find('i').addClass('glyphicon-arrow-left').removeClass('glyphicon-arrow-right');
        } else {
            $(this).find('i').removeClass('glyphicon-arrow-left').addClass('glyphicon-arrow-right');
        }
    });

    $.fn.extend({
        animateCss: function (animationName, callback) {
            var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
            $(this).addClass('animated ' + animationName).one(animationEnd, function () {
                $(this).removeClass('animated ' + animationName);
                if (callback !== undefined && typeof(callback) === 'function') {
                    callback();
                }
            });
        }
    });

    $('.toggle-button').hover(function () {
        $(this).animateCss('pulse');
    }, function () {});

    $.fn.editable.defaults.success = (function (response, newValue) {
        $.growl({message: response['message'], style: response['alert_type'], title: ''});
    });

});

$(window).load(function () {
    setTimeout(function () {
        NProgress.set(0.2);
    }, 200);
    setTimeout(function () {
        NProgress.set(0.4);
    }, 300);
    setTimeout(function () {
        NProgress.set(0.6);
    }, 500);
    setTimeout(function () {
        NProgress.set(0.8);
    }, 550);
    setTimeout(function () {
        NProgress.done();
    }, 600);
});

function addPostThumbnail(targetID, containerID) {
    var target = $('#' + targetID),
        container = $('#' + containerID);

    function changePostThumbnail(image) {
        target.attr('src', image.attr('src'));
        container.val(image.attr('name'));
    }

    if (library == null) {
        library = new mediaLibrary({is_single: true, is_modal: true, callback: changePostThumbnail});
    }
    library.show();
    library.callback = changePostThumbnail;
}

function validateForm(formId, need_submit, callback) {
    if (need_submit === undefined) {
        need_submit = true;
    }
    var form = $('#' + formId), error = false, error_message = '';

    $('.validation-error').each(function () {
        $(this).remove();
    });
    form.find('input, textarea, select').each(function () {

        if ($(this).prop('required') == true) {
            if ($(this).val() == null || $(this).val() == '') {
                error_message = '<p class="text-danger validation-error"><small>Обязательное поле</small></p>';
                error = true;
            } else if ($(this).is(":invalid")) {
                error_message = '<p class="text-danger validation-error">Невелидные данные</p>';
                error = true;
            }
        }

        if ($(this).parent().hasClass('input-group')) {
            $(this).parent().after($(error_message));
        } else {
            $(this).after($(error_message));
        }
        error_message = '';

    });

    if (!error && typeof callback === 'function') {
        callback();
    }

    if (!error && need_submit && typeof callback !== 'function') {
        form.submit();
    }
}

function goToPage(value, inputName) {
    var form = $('#get-page-form');
    form.find('input[name=' + inputName + ']').val(value);
    form.submit();
}

function loadMore(button, scope, url) {
    $.ajax({
        url: url
    }).done(function (result) {
        scope.append(result['data']);
        if (result['last']) {
            button.remove();
        }
    });
}

function toggleCommentEdit(elem, editMode) {
    if (editMode) {
        elem.find('.comment-container').fadeOut();
        elem.find('.comment-edit').fadeIn();
    } else {
        elem.find('.comment-container').fadeIn();
        elem.find('.comment-edit').fadeOut();
    }
}

function createOrder(csrf_token, form) {
    $.ajax({
        url: form.attr('action'),
        method: 'POST',
        data: {data: JSON.stringify(form.serializeArray()), csrfmiddlewaretoken: csrf_token},
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }).done(function (result) {
        if (result['code'] === 200) {
            var counter = $('#basket_items_count'),
                count = result['count'],
                size_count_pk = result['size_count_pk'];

            if (count === 0) {
                $('li#container-size-' + size_count_pk).addClass('disable').removeClass('selected');
                $('input#size-' + size_count_pk).prop('disabled', true).prop('checked', false);
            }
            $('li#container-size-' + size_count_pk).data('count', count);
            selectSize(size_count_pk);

            counter.removeClass('hidden');
            $.growl({message: 'Товар успешно добавлен в корзину', style: 'notice', title: ''});
            counter.html(parseInt(counter.html()) + 1);
        } else if (result['code'] === 401) {
            $.growl({message: 'Вы не выбрали ни одного размера', style: 'warning', title: ''});
        }
    });
}

function selectSize(pk) {
    $('.size-input').removeAttr('checked');
    $('#size-' + pk + ':not([checked]):not([disabled])').attr('checked', true);
    $('.size').removeClass('selected');
    $('#container-size-' + pk).not('.disable').addClass('selected');

    if ($('#container-size-' + pk).data('count') === 1) {
        $('#last-item').removeClass('hidden');
    } else {
        $('#last-item').addClass('hidden');
    }

}

function confirmation(callback, message) {
    message = message === undefined ? "<h4>Вы уверены, что хотите удалить этот предмет?</h4>" : message;
    bootbox.confirm({
        size: 'small',
        message: message,
        callback: function (result) {
            if (result) {
                callback();
            }
        }
    });
}


function changeSlide(item) {
    var productDivs = document.getElementsByClassName('item');
    var previewDivs = document.getElementsByClassName('item-preview');
    if (productDivs && productDivs.length && previewDivs && previewDivs.length) {
        var previewImg = Array.prototype.slice.call(previewDivs, 0)
            .filter(function (el) {
                return el.localName === 'img'
            });

        if (item) {
            $('.img-background').attr('src', item.img);
            $('.img-active').attr('src', item.img);
            $('.item-preview').each(function () {
                if ($(this).attr('src') !== item.img) {
                    $(this).addClass('parts');
                } else {
                    $(this).removeClass('parts');
                }
            });
        }

        previewImg.forEach(function (img, i) {
            img.setAttribute('data-key', i);

            img.addEventListener('click', function (e) {
                const clicked = e.target;
                const i = +clicked.getAttribute('data-key');
                const src = $(this).attr('src');
                $('.img-background').attr('src', src);
                $('.img-active').attr('src', src);
                $(`img[data-key=${i}]`).removeClass("parts");
                for (var j = 0; j < products.length; j++) {
                    if (j !== i) {
                        $(`img[data-key=${j}]`).addClass("parts");
                    }
                }
            })
        });
    }
}

function createItemModal(url, csrf_token){
    $.ajax({
        url: url,
        type: 'GET',
        data: {csrfmiddlewaretoken: csrf_token}
    }).done(function (result) {
        $(result['data']).appendTo($('body'));
        $('#create-item-modal').modal({backdrop: "static"}).modal('show');
    });
}


let websocketConnection = (function(user_pk, recipient_pk){
    var self = this;
    self.user_pk = user_pk;
    self.recipient_pk = recipient_pk ? recipient_pk : user_pk;

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    self.socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat/author/" + self.user_pk + "/recipient/" + (self.recipient_pk == self.user_pk ? '-' : self.recipient_pk) + "/");

});