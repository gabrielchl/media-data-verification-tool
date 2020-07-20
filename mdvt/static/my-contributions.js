for (var i = 0; i < contribs.length; i++) {
    $.ajax({
        url: "https://www.wikidata.org/w/api.php",
        data: {
            "action": "query",
            "format": "json",
            "prop": "pageterms",
            "titles": contribs[i].depict_value,
            "origin": "*"
        },
        count: i,
        contrib: contribs[i],
        success: function(response) {
            $.ajax({
                url: "https://commons.wikimedia.org/w/api.php",
                data: {
                	"action": "query",
                	"format": "json",
                	"pageids": this.contrib.page_id,
                    "origin": "*"
                },
                count: this.count,
                contrib: this.contrib,
                success: function(query_data) {
                    var title = query_data.query.pages[this.contrib.page_id].title;
                    var image_src = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + title + '?width=300';
                    var image_url = 'https://commons.wikimedia.org/wiki/' + title;

                    var depict_label = Object.values(response.query.pages)[0].terms.label[0];

                    var statement = '';

                    switch (this.contrib.type) {
                        case 'P180':
                            statement = 'Is [DEPICT] in the above [MEDIA]?';
                            break;
                        case 'rank':
                            statement = 'Is [DEPICT] porminent in the above [MEDIA]?';
                            break;
                        case 'P2677':
                            statement = 'Is [DEPICT] in the frame in the above [MEDIA]?';
                            break;
                        case 'P1354':
                            statement = 'Is [DEPICT] in the above [MEDIA] shown with [QUALIFIER] (on it)?';
                            break;
                        case 'P462':
                            statement = 'Is [DEPICT] in the above [MEDIA] have the color [QUALIFIER]?';
                            break;
                        case 'P518':
                            statement = 'Is [DEPICT] at the [QUALIFIER] part of the above [MEDIA]?';
                            break;
                        case 'P1114':
                            statement = 'Are there [QUALIFIER] [DEPICT](s) in the above [MEDIA]?';
                            break;
                        case 'P4878':
                            statement = 'Does the [DEPICT] in the above [MEDIA] symbolize [QUALIFIER]?';
                            break;
                        case 'P3828':
                            statement = 'Is [DEPICT] in the above [MEDIA] wearing (a) [QUALIFIER]?';
                            break;
                        case 'P710':
                            statement = 'Is [QUALIFIER] a participant in [DEPICT] in the above [MEDIA]?';
                            break;
                        case 'P1419':
                            statement = 'Is the [DEPICT] in the above [MEDIA] in [QUALIFIER] shape?';
                            break;
                        case 'P6022':
                            statement = 'Is [DEPICT] in the above [MEDIA] having the expression, gesture or body pose [QUALIFIER]?';
                            break;
                        case 'P186':
                            statement = 'Is [QUALIFIER] used in the [DEPICT] in the above [MEDIA]?';
                            break;
                        case 'P1884':
                            statement = 'Does [DEPICT] in the above [MEDIA] have [QUALIFIER]?';
                            break;
                        case 'P1552':
                            statement = 'Is [QUALIFIER] a quality of [DEPICT] in the above [MEDIA]?';
                            break;
                        case 'P1545':
                            statement = 'Does the [DEPICT] in the above [MEDIA] have the series ordinal [QUALIFIER]?';
                            break;
                        case 'P7380':
                            statement = 'Is the [DEPICT] in the above [MEDIA] identified by [QUALIFIER]?';
                            break;
                        case 'P149':
                            statement = 'Is the [DEPICT] in the above [MEDIA] of [QUALIFIER](style)?';
                            break;
                    }

                    statement = statement.replace('[DEPICT]', '<a class="claim-link" href="https://www.wikidata.org/wiki/' + this.contrib.depict_value + '" target="_blank">' +
                                                              '    <span class="claim-id">' +
                                                              '        ' + depict_label +
                                                              '    </span>' +
                                                              '</a>');
                    statement = statement.replace('[MEDIA]', '<a href="' + image_url + '" target="_blank">image</a>');
                    statement = statement + ' ' + this.contrib.answer.charAt(0).toUpperCase() + this.contrib.answer.slice(1);

                    var card = '<div class="col-md-3 my-3" data-order="' + this.count + '">' +
                               '    <div class="card contribution-card">' +
                               '        <a class="img-link" href="' + image_url + '" target="_blank">' +
                               '            <img class="card-img-top" src="' + image_src + '">' +
                               '        </a>' +
                               '        <div class="card-body">';

                    if (this.contrib.contrib_type == 'test') {
                        card += '            <span class="badge badge-secondary">Test Question</span><br>';
                    }

                    card += '            ' + statement + '<br>' +
                                '            <span class="text-muted">' + this.contrib.time_created + '</span>' +
                                '        </div>' +
                                '    </div>' +
                                '</div>';
                    $('#contribs-container').append(card);

                    $('#contribs-container > div').sort(function(a, b) {
                        return a.dataset.order > b.dataset.order;
                    }).appendTo('#contribs-container');
                }
            });
        }
    });
}

var test_showing = true;

$('#test-trigger').click(function() {
    if (test_showing) {
        $('.contribution-card.test-question').parent().hide();
        $('#test-trigger').text('Show Test Questions');
        test_showing = false;
    } else {
        $('.contribution-card.test-question').parent().show();
        $('#test-trigger').text('Hide Test Questions');
        test_showing = true;
    }
})
