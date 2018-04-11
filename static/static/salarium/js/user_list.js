/**
 * Created by 11Linn on 04.06.16.
 */

$(window).ready(function () {
    $('.user-email-delivery').change(function(){
        $.ajax({
            url: $(this).attr('url')
        }).done(function (result) {
            $(this).val(result['data'].toString());
            var message = result['data']? 'добавлен в список' : 'исключен из списка';
            $.growl({ style: 'notice', title: '', message: "Пользователь '" +result['user_name']+ "' успешно " + message + " получателей новостей" });
        });
    });

    $('input#livesearch').liveSearch({
        table : 'table'
    });
});

function change_availability(elem, url){
    if(elem.find('i').hasClass('fa-unlock-alt')){
        bootbox.confirm({
            size: 'small',
            message: "<h3>Вы уверены?</h3>",
            callback: callbackFunction
        });
    }else{
        toggleUserStatus(elem, url);
    }

    function callbackFunction(result) {
        if(result) {
            toggleUserStatus(elem, url);
        }
    }

}

function toggleUserStatus(elem, url){
    $.ajax({
        url: url
    }).done(function (result) {
        $(this).val(result['data'].toString());
        var message = result['data']? 'активирован' : 'заблокирован';
        $.growl({ style: 'notice', title: '', message: "Пользователь '" +result['user_name']+ "' успешно " + message });
    });
    elem.find('i').toggleClass('fa-unlock-alt fa-lock');
    elem.parent().parent().find('.user-status').find('.glyphicon').toggleClass('glyphicon-ok text-success glyphicon-remove text-danger');

}
