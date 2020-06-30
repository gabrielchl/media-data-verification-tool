$('.claim-id').each(function() {
    var replacement = $(this);
    var claim_id = $(this).text();
    $.get("https://commons.wikimedia.org/w/api.php", {
    	"action": "wbgetclaims",
    	"format": "json",
    	"claim": "M91547848$1cb3d7bb-4b35-d1c6-24d0-7c8aaaa0b91d",
        "origin": "*"
    }, function(claim_data) {
        var claim_id = claim_data.claims.P180[0].mainsnak.datavalue.value.id;
        $.get("https://www.wikidata.org/w/api.php", {
        	"action": "wbgetentities",
        	"format": "json",
        	"ids": claim_id,
            "origin": "*"
        }, function(entity_data) {
            replacement.html(entity_data.entities[claim_id].labels.en.value);
        })
    })
});

$('.card-img-top').each(function() {
    var img = $(this);
    var claim_id = $(this).text();
    $.get("https://commons.wikimedia.org/w/api.php", {
    	"action": "query",
    	"format": "json",
    	"pageids": img.attr("src"),
        "origin": "*"
    }, function(query_data) {
        console.log(query_data);
        var title = query_data.query.pages[img.attr("src")].title;
        img.attr("src", 'https://commons.wikimedia.org/wiki/Special:FilePath/' + title + '?width=300');
    })
});
