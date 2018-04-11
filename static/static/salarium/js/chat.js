/**
 * Created by a.sonets on 18.02.17.
 */

var Chat = (function(user_pk, recipient_pk){
    var self = this;

    self.user_pk = user_pk;
    self.recipient_pk = recipient_pk ? recipient_pk : user_pk;
    self.chat = $('#chat-messages-' + self.recipient_pk);
    self.container = $('#user-messages-' + self.recipient_pk);
    self.form = $('#send-message-' + self.recipient_pk);

    self.socket_connection = new websocketConnection(self.user_pk, self.recipient_pk);
    self.socket = self.socket_connection.socket;

    // self.messageTemplate = '<li class="<%self%> clearfix">' +
    // '<span class="chat-img pull-<%self%>" style="padding-right: 5px; padding-left: 5px;">' +
    // '    <img src="<%thumbnail%>" alt="User Avatar" class="img-circle"/>' +
    // '</span>' +
    // '<div class="chat-body clearfix">' +
    // '    <div class="message-header">' +
    // '        <strong class="primary-font"><%username%></strong>' +
    // '        <small class="pull-right text-muted">' +
    // '            <span class="glyphicon glyphicon-time"></span><%date%>' +
    // '        </small>' +
    // '    </div>' +
    // '    <p><%message%></p>' +
    // '</div>' +
    // '</li>';

    self.messageTemplate = '<div class="chatbox__messages__user-message <%self%>">' +
                           '    <div class="chatbox__messages__user-message--ind-message">' +
                           '        <p class="name"><%username%></p>' +
                           '        <br/>' +
                           '        <p class="message"><%message%></p>' +
                           '    </div>' +
                           '</div>';

    $(window).on('keydown', function(e) {
        var msg = self.form.find('input.message').val();
        if (e.which == 13 && e.target.className.indexOf('chat-input') !== -1 && $.trim(msg) !== '') {
            var message = {message: self.form.find('input.message').val()};
            self.socket.send(JSON.stringify(message));
            self.form.find('input.message').val('').focus();
            return false;
        }
    });

    self.init = function(){
        self.scrollChatToBottom();
        self.initSocketHandler();
    };

    self.scrollChatToBottom = function(){
        // self.container.css('max-height', ($(window).height() * 0.8) + 'px');
        self.container.scrollTop(self.container.prop("scrollHeight"));
    };

    self.initSocketHandler = function(){

        self.socket.onmessage = function (message) {
            var data = JSON.parse(message.data);
            var needScroll = self.container.scrollTop() + self.container.height() + 470 >= self.container.prop("scrollHeight");

            var template = self.messageTemplate.replace(/<%self%>/g, data['author_pk'] == self.user_pk ? 'self':'other')
                .replace(/<%thumbnail%>/g, data['thumbnail'])
                .replace(/<%username%>/g, data['username'])
                .replace(/<%date%>/g, data['date'])
                .replace(/<%message%>/g, data['message']);
            var ele = $(template);
            self.chat.append(ele);

            if(self.recipient_pk == data['author_pk']) {
                $('#user-preview-' + self.recipient_pk).removeClass('chatbox__user--away').addClass('chatbox__user--active');
                $('#user-preview-' + self.recipient_pk + ' .badge').removeClass('hidden');
            }
            if(needScroll){
                self.scrollChatToBottom();
            }
        };
    };

    self.init();

});