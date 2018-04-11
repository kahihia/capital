/**
 * Created by linnnai on 6.1.16.
 */
var myTags = [], feeds = null;

function getMultipleTags(tags) {

    var bufferFeeds = [];

    for (var i = 0, len = tags.length; i < len; i++) {
        var newFeed = new Instafeed({
            get: 'tagged',
            tagName: tags[i],
            target: "instafeed",
            clientId: 'c9abbf4211724762bd4058f3def85d8c',
            accessToken: '408015336.c9abbf4.d79b585d9fe24563bfd6535bcd142540',
            limit: Math.floor($('#instafeed').css('width').replace('px', '') / 150) * 3,
            template: '<span class="post"><a href="{{link}}"><img src="{{image}}" />' +
            '</a><span onclick="savePost(this)" class="save-insta-post unsaved"></span></span>'
        });
        bufferFeeds.push(newFeed);

        newFeed.run();
    }
    return bufferFeeds;
}

function loadMore(){

    if (feeds == null){
        feeds = [];
        $('#load-more').html('More...');
    }

    var tagsFromInput = $("#tags-input").tagsinput('items');
    var newTags = [];
    var hasNext = false;

    $.each(tagsFromInput, function(index, value){
        if(myTags.indexOf(value) < 0){
            newTags.push(value);
        }
    });

    $.each(feeds, function(index, feed){
        if (feed.hasNext() && tagsFromInput.indexOf(feed.options.tagName) >= 0) {
            hasNext = true;
            feed.next();
        }
    });

    if(!hasNext && myTags.length > 0){
        $('#more-placeholder a').hide();
    }else if (!$('#more-placeholder a').is(":visible")){
         $('#more-placeholder a').show();
    }

    feeds = feeds.concat(getMultipleTags(newTags));
    myTags = tagsFromInput.slice();

    if(myTags.length == 0) {
        $('#load-more').html('No tags!').prop('disabled', true);
    }else if($('#load-more').html() == 'No tags!' && myTags.length > 0){
        $('#load-more').html('Load').prop('disabled', false);
    }

    if(!$('#clear-all').is(":visible")) {
        $('#clear-all').fadeIn();
    }
}

function savePost(elem) {
    console.log('saving', $(elem).parent().context);
    if ($(elem).hasClass('unsaved')) {
        $(elem).toggleClass('saved unsaved remove');
    }
}

$(window).ready(function () {
    $('#clear-all').hide();

    $('#clear-all').on('click', function(){
        $('#instafeed').empty();
        if($('#clear-all').is(":visible") && $('#instafeed').children().length <= 0) {
            $('#clear-all').fadeOut();
        }
    });

//    function clear(){
//    console.log(123);
//    $('#instafeed').empty();
//}

    $('#tags-input').on('itemAdded', function (event) {
        if($("#tags-input").tagsinput('items').length > 0){
            $('#load-more').prop('disabled', false);
        }

        if(!$('#clear-all').is(":visible") && $('#instafeed').children().length > 0) {
            $('#clear-all').fadeIn();
        }

        $('#more-placeholder a').show();
    });

    $('#tags-input').on('itemRemoved', function (event) {
        if($("#tags-input").tagsinput('items').length == 0){
            $('#load-more').prop('disabled', true);

            if($('#clear-all').is(":visible") && $('#instafeed').children().length <= 0) {
                $('#clear-all').fadeOut();
            }
        }
    });

});