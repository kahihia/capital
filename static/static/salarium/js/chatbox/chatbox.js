let d, h, m, i = 0;

$(document).ready(function () {
    let $messages = $('.messages-content'),
        user_pk = $('.chat').data('user');

    let socket_connection = new websocketConnection(user_pk),
        socket = socket_connection.socket;

    socket.onmessage = function (response) {
        var data = JSON.parse(response.data);
        var message = data['message'];
        if (data.author_pk !== user_pk) {
            insertMessage(message, false, data.thumbnail !== '' ? data.thumbnail : undefined);
        }
    };

    $('.chatbox-toggle-btn').on('click', function(){
        var chatboxBtn = $(this),
            chatbox = $('.chatbox-popup');
        chatboxBtn.animateCss('bounceOut', function(){
            chatboxBtn.addClass('hidden');
            chatbox.removeClass('hidden').animateCss('fadeInRightBig', function(){});
        });
    });

    $('.hide-chatbox.hover-pointer').on('click', function(){
        var chatboxBtn = $('.chatbox-toggle-btn'),
            chatbox = $('.chatbox-popup');
        chatbox.animateCss('fadeOutRightBig', function(){
            chatbox.addClass('hidden');
            chatboxBtn.removeClass('hidden').animateCss('bounceIn', function(){});
        });
    });

    $(document).ready(function () {
        $messages.mCustomScrollbar();

        updateScrollbar();
    });

    function updateScrollbar() {
        $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
          scrollInertia: 10,
          timeout: 0
        });
    }

    function setDate(){
      var d = new Date();
      if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
      }
    }

    function insertMessage(msg, self, thumbnail) {
      if ($.trim(msg) == '') {
        return false;
      }
      $(`<div class="message  ${self ? 'message-personal' : 'new'}">${
          thumbnail ? '<figure class="avatar"><img src="' + thumbnail + '" /></figure>' : ''
      }` + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
    }

    function sendSocketMessage(message){
        if ($.trim(message) == '') {
            return false;
        }
        socket.send(JSON.stringify({'message': message}));
    }

    function sendMessage(self){
        var messageInput = $('.message-input');
        var message = messageInput.val();
        messageInput.val(null).focus();

        sendSocketMessage(message);
        insertMessage(message, self);
    }

    $('.message-submit').click(function() {
        sendMessage(true);
    });

    $(window).on('keydown', function(e) {
        if (e.which == 13 && e.target.className.indexOf('chat-input') !== -1) {
            sendMessage(true);
            return false;
        }
    });
});
