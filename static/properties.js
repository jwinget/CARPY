$('.properties').each(function () {
	var current = $(this);
	current.attr("data-height", current.height());
	});

$('.properties').css("height", "250");
$('.properties_button').html('<a href="#">Expand/Collapse</a>');
$('.properties_button a').attr("href", "javascript:void(0)");

$('.properties_button a').toggle(function() {
	var open_height = $(this).parent().next().next().attr("data-height") + "px";
	$(this).parent().next().next().animate({"height": open_height}, "slow" );
	}, function() {
	$(this).parent().next().next().animate({"height": "250"}, "slow" );
	});
