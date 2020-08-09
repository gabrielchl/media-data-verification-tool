var question_text;

var ready_contribs = [];

function render_contributions_card() {
    for (var i = 0; i < ready_contribs.length; i++) {
        var statement = question_text[ready_contribs[i].question_type];

        statement = statement.replace('[DEPICT]', '<a class="claim-link" href="https://www.wikidata.org/wiki/' + ready_contribs[i].depict_value + '" target="_blank">' +
                                                  '    <span class="claim-id">' +
                                                  '        ' + ready_contribs[i].depict_label +
                                                  '    </span>' +
                                                  '</a>');
        statement = statement.replace('[MEDIA]', '<a href="' + ready_contribs[i].file_page_url + '" target="_blank">image</a>');
        statement = statement + ' ' + ready_contribs[i].answer.charAt(0).toUpperCase() + ready_contribs[i].answer.slice(1);

        var card = '<div class="col-md-3 my-3" data-order="' + i + '">' +
                   '    <div class="card contribution-card">' +
                   '        <a class="img-link" href="' + ready_contribs[i].file_page_url + '" target="_blank">' +
                   '            <img class="card-img-top" src="' + ready_contribs[i].image_url + '">' +
                   '        </a>' +
                   '        <div class="card-body">';

        if (ready_contribs[i].question_type == 'test') {
            card += '            <span class="badge badge-secondary">Test Question</span><br>';
        }

        card += '            ' + statement + '<br>' +
                '            <span class="text-muted">' + ready_contribs[i].time + '</span>' +
                '        </div>' +
                '    </div>' +
                '</div>';
        $('#contribs-container').append(card);

        $('#contribs-container > div').sort(function(a, b) {
            return a.dataset.order > b.dataset.order;
        }).appendTo('#contribs-container');
    }
}

function render_contributions() {
    var ready_count = 0;

    for (var i = 0; i < contribs.length; i++) {
        $.ajax({
            url: "https://www.wikidata.org/w/api.php",
            data: {
                "action": "wbgetentities",
                "format": "json",
                "prop": "labels|descriptions|aliases",
                "ids": contribs[i][10],
                "languages": "en",
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

                        ready_contribs.push({
                            order: this.count,
                            question_type: this.contrib[8],
                            depict_value: this.contrib[10],
                            depict_label: response.entities[this.contrib[10]].labels.en.value,
                            qualifier_value: this.contrib[11],
                            file_page_url: 'https://commons.wikimedia.org/wiki/' + title,
                            image_url: 'https://commons.wikimedia.org/wiki/Special:FilePath/' + title + '?width=300',
                            question_type: this.contrib[8],
                            answer: this.contrib[3],
                            time: this.contrib[5],
                            test_question: this.contrib[13]
                        });

                        ready_count++;

                        if (ready_count == contribs.length) {
                            ready_contribs.sort(
                                function(a, b) {
                                    return a.order - b.order;
                                }
                            )

                            render_contributions_card();
                        }
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
