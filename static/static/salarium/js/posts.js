/**
 * Created by linnnai on 1.5.16.
 */

var libraryMulti = null;

function openMediaLibraryModal() {
    function insertImage(images) {
        if (images.constructor === Array) {
            images.forEach(function (image, index) {
                addImageToEditor(image.attr('src'));
            });
        } else {
            addImageToEditor(images.attr('src'));
        }

    }

    function addImageToEditor(imageSrc) {
        // $('#summernote').summernote('insertImage', imageSrc);
        var src = '<img class="photoblog" src="' + imageSrc + '">';
        $('#summernote').trumbowyg('html', $('#summernote').trumbowyg('html') + src);
    }

    if (libraryMulti == null) {
        libraryMulti = new mediaLibrary({is_single: false, is_modal: true, callback: insertImage});
        libraryMulti.shouldOpen = true;
    }

    libraryMulti.show();
}


$('#summernote').trumbowyg({
    autogrow: true,
    btnsDef: {
        add_image: {
            ico: "insertImage",
            fn: function () {
                openMediaLibraryModal();
            }
        },
        preview: {
            ico: "justifyFull",
            fn: function () {
                openMediaPreviewModal();
            }
        }
    },
    btns: [
        ['viewHTML'],
        ['formatting'],
        'btnGrp-semantic',
        ['superscript', 'subscript'],
        ['link'],
        ['add_image'],
        ['noembed'],
        'btnGrp-justify',
        'btnGrp-lists',
        ['horizontalRule'],
        ['removeformat'],
        ['preview', 'fullscreen']
    ],
    plugins: {
        // Add imagur parameters to upload plugin
        noembed: {
            data: [{"width": 1280, "height": 720}]
        }
    }
});

function openMediaPreviewModal() {
    $('#postPreviewModal').find('#title').html($('#new-post-title').val());
    $('#postPreviewModal').find('#excerpt').html($('#new-post-excerpt').val());
    $('#postPreviewModal').find('#thumbnail').attr('src', $('#new-post-thumbnail').attr('src'));

    var data = formatPostText();
    $('#previewContainer').html(data);
    $('#postPreviewModal').modal({backdrop: "static"}).modal('show');

    $("div.photoblog:not('div.container div.photoblog')").interactive_bg({
        strength: 25,              // Movement Strength when the cursor is moved. The higher, the faster it will reacts to your cursor. The default value is 25.
        scale: 1.02,               // The scale in which the background will be zoomed when hovering. Change this to 1 to stop scaling. The default value is 1.05.
        animationSpeed: "300ms",   // The time it takes for the scale to animate. This accepts CSS3 time function such as "100ms", "2.5s", etc. The default value is "100ms".
        contain: true,             // This option will prevent the scaled object/background from spilling out of its container. Keep this true for interactive background. Set it to false if you want to make an interactive object instead of a background. The default value is true.
        wrapContent: false         // This option let you choose whether you want everything inside to reacts to your cursor, or just the background. Toggle it to true to have every elements inside reacts the same way. The default value is false
    });
}

function formatPostText() {

    var string_src = '<div class="container"><div class="text">' + $('#summernote').trumbowyg('html') + '</div></div>';
    var post_body = $(string_src);
    post_body.find('img.photoblog').each(function () {
        $(this).removeAttr('style');
        var update = '</div></div><div class="photoblog" data-ibg-bg="' + $(this).attr('src') + '"></div><div class="container"><div class="text">';
        var parent = getRootParent($(this));
        string_src = string_src.replace(parent.prop('outerHTML'), parent.prop('outerHTML').replace($(this).prop('outerHTML'), '') + update);
    });
    return string_src;
}

function getRootParent(elem) {
    var res = elem;
    if (!res.parent().hasClass('text')) {
        res = getRootParent(res.parent());
    }
    return res;
}


function savePost() {
    $('#new-post-form').append($('<input type="hidden" name="formatted_body" value=\'' + formatPostText() + '\'>'));

    validateForm('new-post-form');
}
