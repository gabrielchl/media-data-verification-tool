$('.contribution-card').each(function() {
    var claim_label = $(this).find('.claim-id');
    if (claim_label.length) {
        var claim_link = $(this).find('.claim-link');
        var entity_id = claim_label.text();
        $.get("https://commons.wikimedia.org/w/api.php", {
            "action": "wbgetclaims",
        	"format": "json",
            "claim": entity_id,
            "origin": "*"
        }, function(claim_data) {
            var claim_id = claim_data.claims.P180[0].mainsnak.datavalue.value.id;
            claim_link.attr("href", "https://www.wikidata.org/wiki/" + claim_id);
            $.get("https://www.wikidata.org/w/api.php", {
                "action": "wbgetentities",
                "format": "json",
                "ids": claim_id,
                "origin": "*"
            }, function(entity_data) {
                claim_label.html(entity_data.entities[claim_id].labels.en.value);
            });
        });
    }

    var depict_value_label = $(this).find('.depict-value');
    if (depict_value_label.length) {
        var claim_link = $(this).find('.claim-link');
        var depict_value = depict_value_label.text().trim();
        claim_link.attr("href", "https://www.wikidata.org/wiki/" + depict_value);
        $.get("https://www.wikidata.org/w/api.php", {
            "action": "query",
            "format": "json",
            "prop": "pageterms",
            "titles": depict_value,
            "origin": "*"
        }, function(response) {
            depict_value_label.html(Object.values(response.query.pages)[0].terms.label[0]);
        });
    }

    var img = $(this).find('.card-img-top');
    var img_link = $(this).find('.img-link');
    var claim_id = img.text();
    $.get("https://commons.wikimedia.org/w/api.php", {
    	"action": "query",
    	"format": "json",
    	"pageids": img.attr("src"),
        "origin": "*"
    }, function(query_data) {
        var title = query_data.query.pages[img.attr("src")].title;
        img.attr("src", 'https://commons.wikimedia.org/wiki/Special:FilePath/' + title + '?width=300');
        img_link.attr("href", "https://commons.wikimedia.org/wiki/" + title);
    });
});

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
