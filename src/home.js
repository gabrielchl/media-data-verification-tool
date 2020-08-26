$('#category-input').on('input', function() {
    if (!$('#category-input').val().toLowerCase().startsWith('category:')) {
        $('#category-input').val('Category:' + $('#category-input').val());
    }
    $('#filter-category').prop('checked', true);
});

$('#tag-input').on('input', function() {
    $('#filter-tag').prop('checked', true);
});

$('#query-settings-form').submit(function() {
    $('#category-input').val($('#category-input').val().replace(' ', '_'));
    return true;
});

$('#depict-start-btn').click(function() {
    $('#query-settings-form').submit();
})
