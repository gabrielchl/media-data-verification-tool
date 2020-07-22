var question_text;

var question_type = getUrlParam('q-type', undefined);

var filter_type = getUrlParam('filter-type', 'recent');
var filter_value = '';
switch (filter_type) {
    case 'category':
        filter_value = getUrlParam('category');
        break;
    case 'tag':
        filter_value = getUrlParam('tag');
        break;
}

var question_id;
var csrf;

function populate_media_metadata(media_title) {
    $.get({
        url: 'https://commons.wikimedia.org/w/api.php',
        data: {
            'action': 'query',
            'format': 'json',
            'origin': '*',
            'prop': 'imageinfo',
            'titles': media_title,
            'iiprop': 'timestamp|user|extmetadata'
        }
    }).done(function(response) {
        var ext_metadata = Object.values(response.query.pages)[0].imageinfo[0].extmetadata;
        $('#media-desc').html(ext_metadata.ImageDescription.value);
        ext_metadata.Categories.value.split('|').forEach(function(category) {
            $('#media-cats').append('<span class="badge badge-secondary">' + category + '</span> ');
        });
    });
}

function get_media() {
    $.get({
        url: '../api/get-media',
        data: {
            question_type: question_type,
            filter_type: filter_type,
            filter_value: filter_value
        }
    }).done(function(response) {
        if (response.status != 'success') {
            show_toast('warning', 'Failed to get media.');
        } else {
            response = response.data;
            $('.contribute-card').removeClass('loading');
            $('#img-link').attr('href', response.media_page);
            $('.contribute-card .card-img-top').attr('src', 'https://commons.wikimedia.org/wiki/Special:FilePath/' + response.media_title + '?width=500');

            var statement = question_text[response.type];

            statement = statement.replace('[DEPICT]', '<a href="https://www.wikidata.org/wiki/' + response.depict_id + '" target="_blank" data-toggle="popover">' + response.depict_label + '</a>');
            statement = statement.replace('[MEDIA]', '<a href="' + response.media_page + '" target="_blank">' + _('image') + '</a>');
            $('#statement').html(statement);


            $('#media-title').html(response.media_title);
            question_id = response.question_id;
            csrf = response.csrf;

            populate_media_metadata(response.media_title);

            var depict_id = response.depict_id;

            $.get({
                url: 'https://www.wikidata.org/w/api.php',
                data: {
                    'action': 'wbgetentities',
                    'origin': '*',
                    'format': 'json',
                    'ids': depict_id,
                    'languages': 'en',
                    'normalize': 1
                }
            }).done(function(response) {
                var image_title = '';
                if ('P18' in response.entities[depict_id].claims) {
                    image_title = response.entities[depict_id].claims.P18[0].mainsnak.datavalue.value;
                }
                $('[data-toggle="popover"]').popover({
                    trigger: 'hover',
                    html: true,
                    placement: 'top',
                    template: '<div class="popover shadow" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><img class="img-fluid" src="https://commons.wikimedia.org/wiki/Special:FilePath/' + image_title + '"/><div class="popover-body"></div></div>',
                    content: response.entities[depict_id].descriptions.en.value
                });
            });
        }
    });
}

function get_question_text() {
    $.get({
        url: '../api/get-question-text'
    }).done(function(response) {
        question_text = response.data;

        get_media();
    });
}

get_question_text();

function post_contribution(status) {
    $.post({
        url: '../api/contribute',
        data: JSON.stringify({
            question_id: question_id,
            status: status,
            csrf : csrf
        }),
        contentType : 'application/json'
    }).done(function(response) {
        console.log(response);
        show_toast('success', response.data.name);
        $('.contribute-card').addClass('loading');
        $('.contribute-card .card-img-top').attr('src', '');
        $('#media-title').html('');
        $('#media-desc').html('');
        $('#media-cats').html('');
        get_media();
    }).fail(function(response) {
        show_toast('warning', _('Failed to post contribution, please try again.') + response.responseText);
    });
}

function show_toast(status, message) {
    var newToast = $('.' + status + '-toast-template').clone().removeClass(status + '-toast-template');
    newToast.find('.toast-body').text(message);
    newToast.appendTo('#toast-container');
    newToast.toast('show');
}

$('#true-btn').click(function() {
    post_contribution('true');
});

$('#false-btn').click(function() {
    post_contribution('false');
});

$('#skip-btn').click(function() {
    post_contribution('skip');
});
