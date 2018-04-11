/**
 * Created by 11Linn on 27.06.16.
 */

var slidesMediaLibrary = null, newSlider = null;

function Slider(initialize_data){
    var self = this;
    self.slides = [];
    self.html_element = $('#slides');

    self.addSlide = function(slide_data){
        var data = {number: self.slides.length + 1, slider: self};
        _.forEach(slide_data, function (value, key) {
            data[key] = value;
        });
        var newSlide = new Slide(data);
        self.slides.push(newSlide);
        if(slide_data === undefined) {
            self.html_element.append(newSlide.html_element);
        }
        newSlide.bindEvents();
        newSlide.html_element.find('.delete-slide').on('click', function(){
            self.removeSlide(newSlide);
        });
    };

    self.removeSlide = function(slide){
        slide.html_element.remove();
        self.slides = _.without(self.slides, slide);
        _.forEach(self.slides, function(existing_slide){
            if(existing_slide.number >= slide.number) {
                existing_slide.changeNumber(existing_slide.number - 1);
            }
        });
    };

    $('#save-btn').on('click', function(){
        self.save();
    });

    self.save = function(){
        var input = $('#slides-html'), data = [], pk = -1;
        _.forEach(self.slides, function(slide){
            pk = !slide.html_element.find('#pk').length ? -1 : $(this).find('#pk').val();
            var image_src = slide.html_element.find('.new-slide-image').attr('src');
            var object = {pk: pk, image_src: image_src, texts: []};
            _.forEach(slide.texts, function(slide_text){
                slide_text.sliderTextElement.attr('animation', slide_text.html_element.find('select.animation').val());
                slide_text.sliderTextElement.attr('contenteditable', false);
                object.texts.push([slide_text.sliderTextElement.prop('outerHTML').toString(), slide_text.pk]);
            });
            data.push(object);
        });

        input.val(JSON.stringify(data));
        validateForm('new-slider-form');
    };

    self.init = function(){
        $('.list-group-item').each(function(){
            var index = $(this).attr('class').split('-')[$(this).attr('class').split('-').length - 1];
            self.addSlide({html_element: $(this), number: index})
        });
    };

    self.init();
}

function Slide(initialize_data){
    var self = this;
    self.texts = [];
    self.image = null;
    self.slider = initialize_data.slider;
    self.number = initialize_data.number;
    self.html_element =  $(('<li class="list-group-item slide-<%number%>">' +
                    '<div class="panel panel-default" id="size-group-<%number%>">' +
                    '<div class="panel-heading"><h4 class="panel-title text-left">' +
                    '<span><a data-toggle="collapse" href="#collapse-<%number%>" class="size-group-name"><i class="slide-handle glyphicon glyphicon-align-justify"></i><i class="glyphicon glyphicon-chevron-right"></i></a>Slide ' +
                    '<span class="slide-number"><%number%></span></span><a class="pull-right delete-slide"><span class="glyphicon glyphicon-remove text-danger"></span></a></h4></div><div id="collapse-<%number%>" class="panel-collapse collapse">' +
                    '<div class="row add-text-row">' +
                        '<div class="col-xs-12 text-left"><a class="btn btn-primary btn-sm add-text">+ Add text</a></div><hr/>' +
                    '</div>' +
                    '<div class="slide-preview "><a class="change-image">'+
                    '<img src="/static/images/default.png" class="new-brand-thumbnail new-slide-image"/>'+
                    '</a></div>'+
    '</div></div></li>').replace(/<%number%>/g, self.number.toString()));

    self.init = function(){
        self.html_element.find('.slide-text').each(function(){
            var uuid = $(this).attr('id');
            var elem = self.html_element.find('#text-' + uuid);
            var data = {
                html_element: $(this),
                top: elem[0].style.top.replace('px', ''),
                left: elem[0].style.left.replace('px', ''),
                animation: elem.attr('animation'),
                sliderTextElement: elem,
                pk: uuid
            };
            var newText = new Text(self, data);
            self.texts.push(newText);
            newText.bindEvents();
        });
    };

    if (initialize_data.html_element !== undefined){
        self.html_element = initialize_data.html_element;
        self.init();
    }

    self.changeNumber = function(new_number){
        self.html_element.removeClass('slide-' + self.number).addClass(' slide-' + new_number);
        self.html_element.find('#size-group-' + self.number).attr('id', 'size-group-' + new_number);
        self.html_element.find('.size-group-name').attr('href', '#collapse-' + new_number);
        self.html_element.find('.slide-number').text(new_number);
        self.html_element.find('#collapse-' + self.number).attr('id','collapse-' + new_number);
        self.number = new_number;
    };

    self.bindChangeImage = function(){
        self.html_element.find('.change-image').on('click', function(){
            function changeSlideImage(image) {
                self.html_element.find('.new-slide-image').attr('src', image.attr('src'));
            }

            if (slidesMediaLibrary == null) {
                slidesMediaLibrary = new mediaLibrary({is_single: true, is_modal: true, callback: changeSlideImage});
            }
            slidesMediaLibrary.html_element.modal({backdrop: "static"}).modal('show');
            slidesMediaLibrary.callback = changeSlideImage;
        });
    };

    self.bindAddText = function(){
        self.html_element.find('.add-text').on('click', function(){
            var newText = new Text(self);
            self.html_element.find('.add-text-row').after(newText.html_element);
            self.html_element.find('.slide-preview').append(newText.sliderTextElement);
            self.texts.push(newText);
            $('.selectpicker').selectpicker({
                style: 'btn-default',
                size: 4
            });
            newText.bindEvents();
        });
    };

    self.deleteText = function(text){
        text.html_element.remove();
        text.sliderTextElement.remove();
        self.texts = _.without(self.texts, text);
    };

    self.bindEvents = function(){
        self.bindChangeImage();
        self.bindAddText();
    };

}

function Text(slide, init_data){
    var self = this;
    if(init_data === undefined){
        init_data = {};
    }
    self.slide = slide;
    self.pk = init_data.pk === undefined ? Math.random().toString(36).substring(7) : init_data.pk;
    self.text = 'TEXT';
    self.top = init_data.top === undefined ? 10 : init_data.top;
    self.left = init_data.left === undefined ? 10 : init_data.left;
    self.animation = init_data.animation === undefined ? '' : init_data.animation;
    self.html_element = $(('<div class="row slide-text" id="<%pk%>">' +
                    '<div class="col-md-6 col-xs-6 col-sm-6"><div class="input-group"><input type="text" class="form-control position-top" placeholder="Top.."><span class="input-group-addon">%</span></div></div>' +
                    '<div class="col-md-6 col-xs-6 col-sm-6"><div class="input-group"><input type="text" class="form-control position-left" placeholder="Left.."><span class="input-group-addon">%</span></div></div>' +
                    '<div class="col-md-6 col-xs-12 col-sm-12"><select class="selectpicker animation" data-live-search="true"><option value="bounce">bounce</option><option value="flash">flash</option><option value="pulse">pulse</option><option value="rubberBand">rubberBand</option><option value="shake">shake</option><option value="headShake">headShake</option><option value="swing">swing</option><option value="tada">tada</option><option value="wobble">wobble</option><option value="jello">jello</option><option value="bounceIn">bounceIn</option><option value="bounceInDown">bounceInDown</option><option value="bounceInLeft">bounceInLeft</option><option value="bounceInRight">bounceInRight</option><option value="bounceInUp">bounceInUp</option><option value="bounceOut">bounceOut</option><option value="bounceOutDown">bounceOutDown</option><option value="bounceOutLeft">bounceOutLeft</option><option value="bounceOutRight">bounceOutRight</option><option value="bounceOutUp">bounceOutUp</option><option value="fadeIn">fadeIn</option><option value="fadeInDown">fadeInDown</option><option value="fadeInDownBig">fadeInDownBig</option><option value="fadeInLeft">fadeInLeft</option><option value="fadeInLeftBig">fadeInLeftBig</option><option value="fadeInRight">fadeInRight</option><option value="fadeInRightBig">fadeInRightBig</option><option value="fadeInUp">fadeInUp</option><option value="fadeInUpBig">fadeInUpBig</option><option value="fadeOut">fadeOut</option><option value="fadeOutDown">fadeOutDown</option><option value="fadeOutDownBig">fadeOutDownBig</option><option value="fadeOutLeft">fadeOutLeft</option><option value="fadeOutLeftBig">fadeOutLeftBig</option><option value="fadeOutRight">fadeOutRight</option><option value="fadeOutRightBig">fadeOutRightBig</option><option value="fadeOutUp">fadeOutUp</option><option value="fadeOutUpBig">fadeOutUpBig</option><option value="flipInX">flipInX</option><option value="flipInY">flipInY</option><option value="flipOutX">flipOutX</option><option value="flipOutY">flipOutY</option><option value="lightSpeedIn">lightSpeedIn</option><option value="lightSpeedOut">lightSpeedOut</option><option value="rotateIn">rotateIn</option><option value="rotateInDownLeft">rotateInDownLeft</option><option value="rotateInDownRight">rotateInDownRight</option><option value="rotateInUpLeft">rotateInUpLeft</option><option value="rotateInUpRight">rotateInUpRight</option><option value="rotateOut">rotateOut</option><option value="rotateOutDownLeft">rotateOutDownLeft</option><option value="rotateOutDownRight">rotateOutDownRight</option><option value="rotateOutUpLeft">rotateOutUpLeft</option><option value="rotateOutUpRight">rotateOutUpRight</option><option value="hinge">hinge</option><option value="rollIn">rollIn</option><option value="rollOut">rollOut</option><option value="zoomIn">zoomIn</option><option value="zoomInDown">zoomInDown</option><option value="zoomInLeft">zoomInLeft</option><option value="zoomInRight">zoomInRight</option><option value="zoomInUp">zoomInUp</option><option value="zoomOut">zoomOut</option><option value="zoomOutDown">zoomOutDown</option><option value="zoomOutLeft">zoomOutLeft</option><option value="zoomOutRight">zoomOutRight</option><option value="zoomOutUp">zoomOutUp</option><option value="slideInDown">slideInDown</option><option value="slideInLeft">slideInLeft</option><option value="slideInRight">slideInRight</option><option value="slideInUp">slideInUp</option><option value="slideOutDown">slideOutDown</option><option value="slideOutLeft">slideOutLeft</option><option value="slideOutRight">slideOutRight</option><option value="slideOutUp">slideOutUp</option></select></div>' +
                    '<div class="col-md-3 col-xs-6 col-sm-6"><a class="btn btn-sm btn-info animate">Animate</a> </div>' +
                    '<div class="col-md-3 col-xs-6 col-sm-6"><a class="btn btn-sm btn-danger remove-text">Delete</a></div>' +
                    '</div><hr/>').replace(/<%pk%>/g, self.pk));
    self.sliderTextElement = $(('<div class="slider-text editor" id="text-<%pk%>" contenteditable="true" style="top: '+self.top+'px; left: '+self.left+'px">'+self.text+'</div>').replace(/<%pk%>/g, self.pk));

    self.html_element = init_data.html_element === undefined ? self.html_element : init_data.html_element;

    self.sliderTextElement = init_data.sliderTextElement === undefined ? self.sliderTextElement : init_data.sliderTextElement;
    self.sliderTextElement.attr('contenteditable', true);

    self.bindInputs = function(){
        self.html_element.find('select.animation').on('change', function(e){
            self.sliderTextElement.animateCss($(this).val());
        });

        self.html_element.find('.position-top').on('propertychange change input paste', function(){
            self.sliderTextElement.css('top', $(this).val() + '%');
        });

        self.html_element.find('.position-left').on('propertychange change input paste', function(){
            self.sliderTextElement.css('left', $(this).val() + '%');
        });

        self.html_element.find('.btn.animate').on('click', function(){
            self.animation = self.html_element.find('select.animation').val();
            self.sliderTextElement.animateCss(self.html_element.find('select.animation').val());
        });
    };

    self.bindEvents = function(){
        self.html_element.find('.remove-text').on('click', function(){
            self.slide.deleteText(self);
        });

        self.bindInputs();

        self.html_element.find('.position-top').val(self.top);
        self.html_element.find('.position-left').val(self.left);
        self.html_element.find('.animation').selectpicker('val', self.animation);

        $('.editor').popline();
    };
}

function addSlide(){
    if (newSlider !== null){
        newSlider.addSlide();
    }
}

function createSliderModal(url, csrf_token){
    $.ajax({
        url: url,
        type: 'GET',
        data: {csrfmiddlewaretoken: csrf_token}
    }).done(function (result) {
        $(result['data']).appendTo($('body'));
        $('#create-item-modal').modal({backdrop: "static"}).modal('show');
    });
}