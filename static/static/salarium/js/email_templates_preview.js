/**
 * Created by a.sonets on 5/3/17.
 */


$(document).ready(function(){
    $('.selectpicker').on('change', function(){
        console.log($(this).val());
        $('.template-preview').addClass('hidden');
        $('.template-preview.template-' + $(this).val()).removeClass('hidden');
    });
});

function sendEmails(){
    bootbox.confirm({
        size: 'small',
        message: "<h3>Вы уверены?</h3>",
        callback: function(result){ if(result) { $('form.send-emails').submit() } }
    });
}