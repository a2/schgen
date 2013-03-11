;(function ($, window, undefined) {
	$(function() {
		$(document).foundation();

		var selectedCourses = [];
		$(document).on('click', '.course.alert-box .close', function(event) {
			var id = $(this).parents('.course').attr('id'),
				index = selectedCourses.indexOf(id);
			selectedCourses.splice(index, 1);
		});
		$('#search-box').autocomplete({
			source: function(request, response) {
				$.ajax({
					url: '/search.json',
					dataType: 'json',
					data: {
						term: $("#term :checked").attr('name'),
						query: request.term
					},
					success: function(data) {
						console.log(data);
						response(data.results);
						$('#search-box').removeClass('loading-spinner');
					}
				});
			},
			focus: function(event, ui) {
				return false;
			},
			select: function(event, ui) {
				if (selectedCourses.indexOf(ui.item.value) != -1)
				{
					setTimeout(function() {
						var $sect = $('#'+ui.item.value)
							.scrollintoview({ duration: 300 })
							.removeClass('secondary');

						setTimeout(function() {
							$sect.addClass('secondary');
						}, 500);
						
						$('#search-box').val('');
					}, 0);
					return;
				}

				$.ajax({
					url: '/sections.html',
					dataType: 'html',
					data: {
						term: $("#term :checked").attr('name'),
						course: ui.item.value
					},
					success: function(html) {
						$('#accordion').append(html);
						selectedCourses.push(ui.item.value);
						$('#search-box').val('');
					}
				})
			},
			search: function(event, ui) {
				$('#search-box').addClass('loading-spinner');
			},
		})
		.data('ui-autocomplete')._renderItem = function(ul, item) {
			return $('<li />')
				.append(['<a><span class="title">', item.title, '</span><br /><span class="subtitle">', item.subtitle, '</span></a>'].join(''))
				.appendTo(ul);
		};

		$('#search-button').click(function(event) {
			$('#search-box').autocomplete('search', $('#search-box').val());
			event.preventDefault();
		});
	});
})(jQuery, this);

/* 
 * To Title Case 2.0.1 – http://individed.com/code/to-title-case/
 * Copyright © 2008–2012 David Gouch. Licensed under the MIT License. 
 */

String.prototype.toTitleCase = function () {
  var smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|vs?\.?|via)$/i;

  return this.replace(/([^\W_]+[^\s-]*) */g, function (match, p1, index, title) {
    if (index > 0 && index + p1.length !== title.length &&
      p1.search(smallWords) > -1 && title.charAt(index - 2) !== ":" && 
      title.charAt(index - 1).search(/[^\s-]/) < 0) {
      return match.toLowerCase();
    }

    if (p1.substr(1).search(/[A-Z]|\../) > -1) {
      return match;
    }

    return match.charAt(0).toUpperCase() + match.substr(1);
  });
};
