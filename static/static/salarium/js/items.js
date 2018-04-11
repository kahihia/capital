/**
 * Created by 11Linn on 24.06.16.
 */

var gallery = null, galleryLibrary = null;

function initItemController(){
    $('#size-group').on('changed.bs.select', function(){
        toggleItemCount($(this).val());
    });

    toggleItemCount($('#size-group').val());
}

function toggleItemCount(sizeGroupPk){
    console.log(sizeGroupPk);
    $('.size-item').each(function(){
        $(this).addClass('hidden');
    });
    var currentSizeGroup = $('#size-group-' + sizeGroupPk);
    currentSizeGroup.removeClass('hidden');
    currentSizeGroup.find( ":checkbox" ).on('change', function(){
        var input = currentSizeGroup.find( "input[name='"+ $(this).attr('name') + "-value']" );
        input.prop('required', !input.prop('required'))
    });
}

function initBloodHound(){
    var tags_source = $('#all-tags').val().toString().trim().split(',');

    var tags = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // `states` is an array of state names defined in "The Basics"
        local: $.map(tags_source, function(tag){
            return {name: tag};
        })
    });

    tags.initialize();

    $('#tags-input').tagsinput({
        typeaheadjs: [{
            minLength: 1,
            highlight: true
        }, {
            minength: 1,
            name: 'tags',
            displayKey: 'name',
            valueKey: 'name',
            source: tags.ttAdapter()
        }],
        freeInput: true
    });
}

var itemGallery = (function(){
    var self = this;
    self.element = $('#item-gallery-container');
    self.images = [];

    self.addImagesToGallery = function(images){
        if (!Array.isArray(images)){
            images = [images];
        }

        var selected_images = _.filter($('#new-item-images-container').val().split(','), function(img_pk){ return img_pk !== '' });
        images.forEach(function(image){
            if (selected_images.indexOf(image.attr('name')) === -1) {
                self.images.push(image);
                self.addImageToGalleryContainer(image);
            }
        });
    };

    self.addImageToGalleryContainer = function(image){
        var target = $('<span class="item-image"><span class="badge badge-important topcorner delete-item"><i class="glyphicon glyphicon-trash"></i></span></span>');
        image.appendTo(target);
        target.appendTo(self.element);
    };
});

function addImageToItem(containerID){
    if(gallery === null) {
        gallery = new itemGallery();
    }

    var target = $('<div class="item-image" style="width: 50px; height: 50px; padding: 5px;"></div>'),
        container = $('#' + containerID);

    function addImages(images, deselected) {
        var already_selected = _.filter($('#new-item-images-container').val().split(','), function(img_pk){ return img_pk !== '' });
        _.forEach(already_selected, function(image_pk, index){
            if (deselected.indexOf(image_pk) > -1){
                $('#item-gallery-container').find('img[name="' + image_pk + '"]').parent().remove();
            }
        });

        gallery.addImagesToGallery(images);

        var data = [];
        $('.item-image').each(function(){
            data.push($(this).find('img').attr('name'));
        });
        container.val(data.join(','));
    }

    if (galleryLibrary === null) {
        galleryLibrary = new mediaLibrary({is_single: false, is_modal: true, callback: addImages});
    }

    var selected_images = _.filter($('#new-item-images-container').val().split(','), function(img_pk){ return img_pk !== '' });

    galleryLibrary.width = target.width();
    galleryLibrary.height = target.height();
    galleryLibrary.selected_items = selected_images;
    galleryLibrary.selectItems();
    galleryLibrary.html_element.modal({backdrop: "static"}).modal('show');
}

$(document).on('hidden.bs.modal', '#create-item-modal', function () {
    $('#create-item-modal').remove();
});

$(document).on('click', '#item-gallery-container', function(){
    addImageToItem('new-item-images-container');
});

$(document).on('click', '.delete-item', function(e){
    e.preventDefault();

    var container = $('#new-item-images-container');
    var selectedImages = _.filter(container.val().split(','), function(img_pk){ return img_pk !== '' });
    var item_pk = $(this).parent().find('img').attr('name');
    container.val(_.filter(selectedImages, function(pk){ return pk !== item_pk }).join(','));

    $(this).parent().remove();

    return false;
});