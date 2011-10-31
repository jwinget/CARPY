$('.feedback_button a').click(function() {
	$('.feedback').fadeToggle('slow');
	if ($('.feedback_b').hasClass('on')) {
		$('.feedback_b').removeClass('on').addClass('off').text('feedback');
		} else if ($('.feedback_b').hasClass('off')) {
		$('.feedback_b').removeClass('off').addClass('on').text('close');
														        }
	return false;
	});
$(function() {
	$('.feedback_submit').click(function() {
		$.post("{{ url_for('feedback') }}", { comment: $('input.comment').val(), sender: $('input.feedback_email').val() },
			function() {
				$('.feedback').fadeToggle('slow');
				if ($('.feedback_b').hasClass('on')) {
					$('.feedback_b').removeClass('on').addClass('off').text('feedback');
					} else if ($('.feedback_b').hasClass('off')) {
					$('.feedback_b').removeClass('off').addClass('on').text('close');
								}
					}
			);
		return false;
		}
	)});
