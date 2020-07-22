var question_text;

function render_contributions() {
    for (var i = 0; i < contribs.length; i++) {
        $.ajax({
            url: "https://www.wikidata.org/w/api.php",
            data: {
                "action": "query",
                "format": "json",
                "prop": "pageterms",
                "titles": contribs[i][10],
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
                    	"pageids": this.contrib[7],
                        "origin": "*"
                    },
                    count: this.count,
                    contrib: this.contrib,
                    success: function(query_data) {
                        var title = query_data.query.pages[this.contrib[7]].title;
                        var image_src = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + title + '?width=300';
                        var image_url = 'https://commons.wikimedia.org/wiki/' + title;

                        var depict_label = Object.values(response.query.pages)[0].terms.label[0];

                        var statement = question_text[this.contrib[8]];

                        statement = statement.replace('[DEPICT]', '<a class="claim-link" href="https://www.wikidata.org/wiki/' + this.contrib[10] + '" target="_blank">' +
                                                                  '    <span class="claim-id">' +
                                                                  '        ' + depict_label +
                                                                  '    </span>' +
                                                                  '</a>');
                        statement = statement.replace('[MEDIA]', '<a href="' + image_url + '" target="_blank">image</a>');
                        statement = statement + ' ' + this.contrib[3].charAt(0).toUpperCase() + this.contrib[3].slice(1);

                        var card = '<div class="col-md-3 my-3" data-order="' + this.count + '">' +
                                   '    <div class="card contribution-card">' +
                                   '        <a class="img-link" href="' + image_url + '" target="_blank">' +
                                   '            <img class="card-img-top" src="' + image_src + '">' +
                                   '        </a>' +
                                   '        <div class="card-body">';

                        if (this.contrib[13] == 'test') {
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
}

function get_question_text() {
    $.get({
        url: '../api/get-question-text'
    }).done(function(response) {
        question_text = response.data;
        render_contributions();
    });
}

get_question_text();
