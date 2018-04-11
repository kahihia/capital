/**
 * Created by 11Linn on 05.06.16.
 */

$(document).ready(function () {
});

function createSize(formId, containerId, csfr_token) {
    var form = $('#' + formId), container = $('#' + containerId), input = form.find('input[name=name]'),
        data = {name: input.val(), csrfmiddlewaretoken: csfr_token};

    $.ajax({
        url: form.attr('action'),
        type: 'POST',
        data: data
    }).done(function (result) {
        if (result['alert_type'] != 'error') {
            container.prepend($(result['data']));
            input.val('');
        }
        $.growl({message: result['message'], style: result['alert_type'], title: ''});
    });

}

function newSaleAction(containerId, url, action, csrf_token) {
    var container = $('#' + containerId);
    if (action == 'create') {
        createSale(container, url, csrf_token);
    } else if (action == 'delete') {
        deleteSale(container, url, csrf_token);
    }
}

function deleteSale(container, url, csrf_token) {
    $.ajax({
        url: url,
        type: 'POST',
        data: {csrfmiddlewaretoken: csrf_token}
    }).done(function (result) {
        if (result['alert_type'] != 'error' || result['code'] == 404) {
            container.remove();
        }
        if (!$('.sale-container').length) {
            $('.sale-no-data-message').show();
        }
        $.growl({message: result['message'], style: result['alert_type'], title: ''});
    });
}

function createSale(url, csrf_token) {
    var form = $('<form class="hidden-form" action="' + url + '" method="POST">' +
        '<input type="text" name="name" value="' + $('#new-sale-name').val() + '">' +
        '<input type="text" name="date_of_start" value="' + $('#new-sale-date-of-start').val() + '">' +
        '<input type="text" name="date_of_end" value="' + $('#new-sale-date-of-end').val() + '">' +
        '<input type="text" name="rate" value="' + $('#new-sale-rate').val() + '">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrf_token + '"></form>');
    $('body').append(form);
    $('.hidden-form').submit();
}

function createItem(url, csrf_token) {
    $.ajax({
        url: url,
        type: 'GET',
        data: {csrfmiddlewaretoken: csrf_token}
    }).done(function (result) {
        $(result['data']).appendTo($('body'));
        $('#create-item-modal').modal({backdrop: "static"}).modal('show');
        $('.selectpicker').selectpicker({
            style: 'btn-default',
        });
        initBloodHound();
        initItemController();
    });
}
