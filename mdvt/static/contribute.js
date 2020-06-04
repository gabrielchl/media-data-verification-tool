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

var current_claim;
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

$.get({
    url: '../api/get-media',
    data: {
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
        $('#statement').html('<a href="https://www.wikidata.org/wiki/' + response.depict_id + '" target="_blank" data-toggle="popover">' + response.depict_label + '</a> can be seen in the above <a href="' + response.media_page + '" target="_blank">image</a>');
        $('#media-title').html(response.media_title);
        current_claim = response.claim_id;
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
                template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><img class="img-fluid" src="https://commons.wikimedia.org/wiki/Special:FilePath/' + image_title + '"/><div class="popover-body"></div></div>',
                content: response.entities[depict_id].descriptions.en.value
            });
        });
    }
});

function post_contribution(status) {
    $.post({
        url: '../api/contribute',
        data: JSON.stringify({
            type: 'P180',
            data: {
                claim_id: current_claim,
                status: status
            },
            csrf : csrf
        }),
        contentType : 'application/json'
    }).done(function(response) {
        console.log(response);
        show_toast('success', 'Theoretically your contribution is recorded.');
    }).fail(function(response) {
        show_toast('warning', 'Failed to post contribution, please try again.');
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
