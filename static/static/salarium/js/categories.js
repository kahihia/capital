/**
 * Created by 11Linn on 04.06.16.
 */
$(window).ready(function () {
    $('input#livesearch').liveSearch({
        table : 'table' // table selector
    });
});

function closeCategoryEditing(category_id){
    var categoryRow = $('#' + category_id),
        categoryName = categoryRow.find('.category-name');
        categoryName.show();

    categoryRow.find('.category-edit-group').remove();
}

function updateCategory(category_id){
    var categoryRow = $('#' + category_id),
        categoryName = categoryRow.find('.category-name'),
        categoryEditForm = categoryRow.find('.category-edit-group');
        categoryName.html(categoryEditForm.find('input').val()).show();

    $.ajax({
        url: categoryRow.attr('url'),
        data: {'name': categoryEditForm.find('input').val(), 'action': 'update'}
    }).done(function (result) {
        categoryName.html(result['category_name']);
        $.growl({ message: "Категория обновлена", style: 'notice', title: '' });
    });

    categoryEditForm.remove();
}

function deleteCategory(category_id){
    var categoryRow = $('#' + category_id);

    function callbackFunction(result) {
        if(result) {
            $.ajax({
                url: categoryRow.attr('url'),
                data: {'action': 'delete'}
            }).done(function (result) {
                categoryRow.parent().remove();
                $.growl({ message: "Категория удалена", style: 'warning', title: '' });
            });
        }
    }

    bootbox.confirm({
        size: 'small',
        message: "<h3>Вы уверены?</h3>",
        callback: callbackFunction
    });
}