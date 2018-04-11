/**
 * Created by 11Linn on 21.08.16.
 */

$(document).ready(function(){
    //$.growl({message: response['message'], style: response['alert_type'], title: ''});

});

function markAsModerated(element, url){
    baseModerateRequest(element, url, 'Комментарий успешно прошел модерацию', {});
}

function deleteComment(element, url){

    bootbox.confirm({
        size: 'small',
        message: "<h3>Вы уверены?</h3><br><h4 class='text-muted'>Вы не сможете восстановить комментарий</h4>",
        callback: function(result){ if(result){baseModerateRequest(element, url, 'Комментарий успешно удален', {});} }
    });
}

function moderateComment(element, url){
    var data = {
        comment_body: $('#edited_comment_body').val()
    };

    baseModerateRequest(element, url, 'Комментарий успешно отредактирван', data);
}

function baseModerateRequest(element, url, text, data){
    $.ajax({
        url: url,
        data: data,
        method: 'POST'
    }).done(function (result) {
        $.growl({message: text, style: 'notice', title: ''});
        toggleCommentEdit(element.find('.media-body'), false);
        element.animateCss('fadeOutLeft', function(){ element.remove(); });
    });
}