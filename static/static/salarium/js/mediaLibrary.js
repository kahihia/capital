var uploader = null;
let imageHtml = '<span class="image-thumbnail image-context-menu">' +
                            '<%image%>' +
                            '<span class="additional unselected"></span>' +
                        '</span>';

function mediaLibrary(initialize_data){
    var self = this;

    self.is_single = false;
    self.callback = null;
    self.width = 100;
    self.height = 100;
    self.is_modal = false;
    self.images = [];
    self.slides = [];
    self.gallery = {};
    self.page = 2;
    self.selected_items = [];

    $.each(initialize_data, function(key, value){
        self[key] = value;
    });

    self.init = function(){
        self.findHTMLElement();
        if(self.is_modal && !self.html_element.length) {
            self.loadModalLibrary();
        }else{
            self.collectMedia();
            self.bindEvents();
        }
    };

    self.loadAlbumImages = function(album_pk, elem){
        $.ajax({
            url: '/media_library/album/' + album_pk
        }).done(function (result) {
            let images = result.images;

            _.forEach(images, function(image){
                let img = $(imageHtml.replace('<%image%>', image));

                if (!elem){
                    elem = self.html_element.find('.media-placeholder').find('#album-'+ album_pk);
                }

                elem.find('div.panel-body').append(img);
                let media = new mediaObject(self, img);
                if(self.is_single) {
                    self.bindEventToNewMediaObject(media);
                }

                if(self.selected_items.indexOf(media.public_id) > -1){
                    media.select();
                }

                self.images.push(media);
            });
        });
    };

    self.addSlide = function(image){
        var tempImage1 = new Image();
        tempImage1.src = image.attr('src');
        tempImage1.onload = function() {
            self.slides.push({src: tempImage1.src,
                              w: tempImage1.width,
                              h: tempImage1.height,
                              public_id: image.attr('name'),
                              album_id: image.data('album-id'),
            });
        };
    };

    self.show = function(){
        self.html_element.css('z-index', '9999999999');
        self.html_element.modal({backdrop: "static"}).modal('show');
    };

    self.loadModalLibrary = function(){
        $.ajax({
            url: '/media_library/modal_library'
        }).done(function (result) {
            $("body").append(result['data']);
            self.findHTMLElement();
            self.show();

            self.html_element.on('hidden.bs.modal', function () {
                self.deselectAll();
            });

            self.collectMedia();
            self.bindEvents();
        });
    };

    self.findHTMLElement = function(){
        self.html_element = $('#mediaLibrary');
        self.loadMore = self.html_element.find('#load-more');

        if(self.html_element.length){
            self.key = Math.random().toString(36).substring(7);
            self.html_element.attr('id', self.html_element.attr('id') + self.key);

            self.html_element.find('.collapse').each(function(){
                var id = $(this).attr('id');
                $(this).attr('id', id + '-' + self.key);
            });

            self.html_element.find('.collapse-toggle').each(function(){
                var href = $(this).attr('href');
                $(this).attr('href', href + '-' + self.key);
            });

        }
    };

    self.loadMoreImages = function(){
        $.ajax({
            url: '/media_library/library/images/' + self.page
        }).done(function (result) {
            self.page++;
            let images = result.images;

            _.forEach(images, function(image){
                let img = $(imageHtml.replace('<%image%>', image));
                self.html_element.find('.media-placeholder').append(img);
                let media = new mediaObject(self, img);
                if(self.is_single) {
                    self.bindEventToNewMediaObject(media);
                }
                self.images.push(media);
            });
        });
    };

    self.bindUploader = function(){
        if(uploader === null) {
            uploader = new mediaUploader(self);
        }
        self.media_uploader = uploader;
        
        self.html_element.find('#upload-media').on('click', function(){
            self.media_uploader.uploader_element.modal({backdrop: "static"}).modal('show');
        });
    };

    self.deleteMediaItems = function(object){
        var items_public_ids = [];
        if(object === undefined) {
            $.each(self.images, function (index, image) {
                if (image.selected) {
                    items_public_ids.push(image.public_id);
                }
            });
        }else{
            items_public_ids = [object.find('img').attr('name')];
        }

        $.ajax({
            url: '/media_library/delete',
            method: 'POST',
            data: {'public_ids': JSON.stringify(items_public_ids)}
        }).done(function (result) {
            $.each(result['deleted'], function(index, public_id) {
                $.each(self.images, function(index, image) {
                    if (image !== undefined && image.public_id == public_id) {
                        image.object.remove();
                        image = null;
                        delete self.images[index];
                        self.images.splice(index, 1);
                    }
                });
            });
        });
    };

    self.deleteItems = function(key, options){
        var trigger = undefined;
        if (options !== undefined) {
            trigger = options.$trigger;
        }
        if(_.findIndex(self.images, {selected: true}) >= 0 || options !== undefined) {
            bootbox.confirm({
                size: 'small',
                message: "<h3>Вы уверены?</h3>",
                callback: function(result){ if(result){ self.deleteMediaItems(trigger); } }
            });
        }
    };

    self.loadFullSizeImage = function(public_id, album_id, index, async){
        if (async === undefined){
            async = true;
        }

        var deferred = $.Deferred();

        if(index !== null) {
            $.ajax({
                async: async,
                cache: false,
                type: "GET",
                url: '/media_library/get_image',
                data: {
                    'width': 'NaN',
                    'height': 'NaN',
                    'public_id': public_id,
                    'album_id': album_id,
                },
                success: function (result) {
                    let tempImage1 = new Image();
                    tempImage1.src = $(result['image']).attr('src');
                    tempImage1.onload = function () {
                        self.slides[index] = {
                            src: tempImage1.src,
                            w: tempImage1.width,
                            h: tempImage1.height,
                            hi_res_loaded: true,
                            public_id: public_id,
                            album_id: album_id,
                            fullSizedImage: $(result['image'])
                        };

                        self.images[index].fullSizedImage = $(result['image']);

                        if (typeof(self.gallery.invalidateCurrItems) === 'function') {
                            self.gallery.invalidateCurrItems();
                            self.gallery.updateSize(true);
                        }

                        deferred.resolve();
                    };
                }
            });
        }
        return deferred.promise();
    };

    self.openInitedGallery = function(index){
        var pswpElement = document.querySelectorAll('.pswp')[0];

        var gallery_options = {
            index: index
        };

        self.gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, self.slides, gallery_options);

        self.gallery.listen('beforeChange', function(index, item) {
            let public_id = self.gallery.currItem.public_id;
            let album_id = self.gallery.currItem.album_id;
            if (!self.gallery.currItem.hi_res_loaded) {
                self.loadFullSizeImage(public_id, album_id, _.findIndex(self.slides, {public_id: public_id}));
            }
        });

        self.gallery.init();
    };

    self.openGallery = function(key, options){
        var public_id = options.$trigger.find('img').attr('name'),
            album_id = options.$trigger.find('img').data('album_id'),
            index = _.findIndex(self.slides, {public_id: public_id});

        if(!self.slides[index].hi_res_loaded) {
            self.loadFullSizeImage(public_id, album_id, index);
            self.openInitedGallery(index);
        }else{
            self.openInitedGallery(index);
        }
    };

    self.bindDelete = function(){
        self.html_element.find('#delete-media').on('click', function(){
            self.deleteItems();
        });
    };

    self.selectItems = function(){
        _.forEach(self.images, function(image){
            if(self.selected_items.indexOf(image.public_id) !== -1) {
                image.select();
            }
        })
    };

    self.deselectAll = function(){
        _.forEach(self.images, function(image){
            image.deselect();
        })
    };

    self.bindCallback = function(){
        var loaders = [];

        self.html_element.find('#select-button').on('click', function(){
            if (typeof self.callback === "function") {
                var selectedImages = [];
                var deselected = _.map(_.filter(self.images, function(img){ return !img.selected }), function(img){ return img.public_id });
                self.images.forEach(function(image){
                    if(image.selected){
                        if (image.fullSizedImage && image.fullSizedImage !== null) {
                            selectedImages.push(image.fullSizedImage);
                        }else{
                            var loader = self.loadFullSizeImage(image.public_id, image.album_id, _.indexOf(self.images, image), false);
                            loaders.push(loader);

                            $.when.apply(null, [loader]).done(function() {
                                self.callback(self.is_single ? image.fullSizedImage : [image.fullSizedImage], deselected);
                            });
                        }
                    }
                });
                if (selectedImages.length > 0) {
                    $.when.apply(null, loaders).done(function () {
                        self.callback(self.is_single ? selectedImages[0] : selectedImages, deselected);
                    });
                }

            }
            self.deselectAll();
            self.html_element.modal('hide');
        });
    };

    self.bindEvents = function(){
        if(self.is_modal){
            self.bindCallback();
        }
        self.bindUploader();
        self.bindDelete();

        self.loadMore.on('click', function(){
            self.loadMoreImages();
        });

        self.html_element.find('.collapse').on('show.bs.collapse', function () {
            if(!$(this).find('img').length) {
                self.loadAlbumImages($(this).data('album-pk'), $(this));
            }
        });
    };

    self.loadContextMenu = function() {
        $.contextMenu({
            // define which elements trigger this menu
            selector: ".image-context-menu",
            // define the elements of the menu
            items: {
                foo: {name: "Show", callback: self.openGallery},
                bar: {name: "Delete", callback: self.deleteItems, icon: "delete"}
            }
            // there's more, have a look at the demos and docs...
        });
    };

    self.collectMedia = function(){
        self.html_element.find('.image-thumbnail').each(function(){
            var media = new mediaObject(self, $(this));
            if(self.is_single) {
                self.bindEventToNewMediaObject(media);
            }

            if(self.selected_items.indexOf(media.public_id) > -1){
                media.select();
            }

            self.images.push(media);
        });
        self.loadContextMenu();
    };

    self.bindEventToNewMediaObject = function(media){
        media.object.find('.additional').on('click', function () {
            self.images.forEach(function(object) {
                if(object.selected){
                    object.deselect();
                }
            });
            media.select();
        });
    };

    self.addUploadedMedia = function(newMedia){
        self.html_element.find('.media-placeholder').append(newMedia);
        var uploadedMedia = new mediaObject(this, newMedia);
        if(self.is_single) {
            self.bindEventToNewMediaObject(uploadedMedia);
        }
        self.images.push(uploadedMedia);
    };


    self.init();

}

var mediaObject = (function(library, object){
    var self = this;

    self.library = library;
    self.object = object;
    self.public_id = object.find('img').attr('name');
    self.album_id = object.find('img').data('album_id');
    self.fullSizedImage = null;

    self.selected = self.object.find('.additional').hasClass('selected');

    self.toggleSelection = function(){
        self.object.find('img').toggleClass('selected-item');
        self.object.find('.additional').toggleClass('selected unselected');
        self.selected = !self.selected;
    };

    self.select = function(){
        self.object.find('img').addClass('selected-item');
        self.object.find('.additional').addClass('selected').removeClass('unselected');
        self.selected = true;
    };

    self.deselect = function(){
        self.object.find('img').removeClass('selected-item');
        self.object.find('.additional').removeClass('selected').addClass('unselected');
        self.selected = false;
    };

    self.addToGallery = function(){
        self.library.addSlide(self.object.find('img'));
    };

    self.addToGallery();
    self.object.find('.additional').on('click', self.toggleSelection);

});

var mediaUploader = (function(mediaLibrary, callback){

    var self = this;
    self.mediaLibrary = mediaLibrary;
    self.callback = callback;

    var html_data = '<div class="modal fade" id="mediaUploader" role="dialog"><div class="modal-dialog modal-lg">' +
        '<div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button>' +
        '<h4 class="modal-title">Загрузка картинок</h4></div><div class="modal-body">' +
        '<form action="/media_library/upload/" class="dropzone">' +
        '</form></div><div class="modal-footer">' +
        '<button type="button" class="btn btn-default" data-dismiss="modal">Закрыть</button></div></div></div></div>';

    $('body').append(html_data);

    self.uploader_element = $('#mediaUploader');

    self.show = function(){
        self.uploader_element.modal({backdrop: "static"}).modal('show');
    };

    self.hide = function(){
        self.uploader_element.modal('hide');
    };

    function initMediaUploader(){
        Dropzone.autoDiscover = false;
        if (typeof self.dropzone == typeof undefined) {
            self.dropzone = new Dropzone(".dropzone");
        }
        self.dropzone.on("success", function (file, data) {
            if (typeof(self.callback) === 'function'){
                self.callback(data);
            }else if(self.mediaLibrary !== undefined) {
                self.mediaLibrary.addUploadedMedia($('<span class="image-thumbnail image-context-menu">' + data['image'] + '<span class="additional unselected"></span></span>'));
            }
        });
    }

    initMediaUploader();
});
