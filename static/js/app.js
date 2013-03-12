;(function ($, window, undefined) {
	$(function() {
		$(document).foundation();
		var columbiaDays = "UMTWRFS",

			calendar = $('#calendar'),

			eventLists = {
				busyTimes: []
			},
			selectedEventListIndex = 0;

		function updateBusyTimes() {
			eventLists.busyTimes = $.grep(calendar.fullCalendar('clientEvents'), function(calendarEvent) {
				if (calendarEvent.url)
					return null;
				else
					return calendarEvent;
			});
		}
		calendar.fullCalendar({
			events: function(start, end, callback) {
				var events = eventLists.busyTimes;
				if (eventLists.eventLists && selectedEventListIndex < eventLists.eventLists.length)
					events = events.concat(eventLists.eventLists[selectedEventListIndex]);
				callback(events);
			},
			defaultView: 'agendaWeek',
			header: null,
			columnFormat: { agendaWeek: 'ddd' },
			allDaySlot: false,
			year: 1970,
			month: 0,
			date: 4,
			minTime: '8:00am',
			maxTime: '10:00pm',
			allDayDefault: false,
			editable: true,
			selectable: true,
			selectHelper: true,
			contentHeight: 1500,
			eventBackgroundColor: '#CB502B',
			select: function(start, end, allDay) {
				calendar.fullCalendar('renderEvent', {
					title: "Unavailable",
					start: start,
					end: end,
					allDay: allDay
				}, false).fullCalendar('unselect');

				updateBusyTimes();
			},
			eventClick: function(calendarEvent) {
				if (calendarEvent.url) {
					window.open(event.url);r
					return false;
				}

				var busyTimes = eventLists.busyTimes,
					index = busyTimes.indexOf(calendarEvent);
				busyTimes.splice(index, 1);
				eventLists.busyTimes = busyTimes;

				calendar.fullCalendar('removeEvents',
					calendarEvent.id || calendarEvent._id);
				updateBusyTimes();
			},
			eventDrop: function(calendarEvent, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, ui, view ) {
				var start = calendarEvent.start,
					end = calendarEvent.end;

				function trimStart() {
					start = new Date(end.getTime());
					start.setHours(8);
					start.setMinutes(0);

					calendarEvent.start = start;
					calendar.fullCalendar('updateEvent', calendarEvent);
				}

				function trimEnd() {
					end = new Date(start.getTime());
					end.setHours(22);
					end.setMinutes(0);
					
					calendarEvent.end = end;
					calendar.fullCalendar('updateEvent', calendarEvent);
				}

				if (start.getDay() != end.getDay()) {
					if (minuteDelta > 0) {
						trimEnd();
					} else {
						trimStart()
					}
				}
				else if (start.getHours() < 8)
					trimStart();
				else if (end.getHours() > 22 || (end.getHours() == 22 && end.getMinutes() > 0))
					trimEnd();

				updateBusyTimes();
			},
			eventResize: function(calendarEvent, dayDelta, minuteDelta, revertFunc, jsEvent, ui, view) {
				updateBusyTimes();
			}
		});
		
		function toggleAll(el, checked) {
			var $section = $(el).parents('[data-alert]'),
				$checkboxes = $section.find('.custom.checkbox');
			if (checked)
				$checkboxes.addClass('checked');
			else
				$checkboxes.removeClass('checked');
			$section.find('input[type=checkbox]').prop('checked', !!checked);
		}

		function updateNavigationTitle() {
			var length = eventLists.eventLists ? eventLists.eventLists.length : 0,
				prev = $('.nav-prev .button'),
				next = $('.nav-next .button');

			$('.nav-title').text(length ? ("Schedule " + (selectedEventListIndex + 1) + " / " + length) : "No Schedules");
			
			console.log(selectedEventListIndex, length);

			if (selectedEventListIndex == 0)
				prev.addClass('disabled');
			else
				prev.removeClass('disabled');

			if (length == 0 || selectedEventListIndex == length - 1)
				next.addClass('disabled');
			else
				next.removeClass('disabled');
		}
		updateNavigationTitle();

		$('.nav-prev .button').click(function(event) {
			event.preventDefault();
			if ($(this).hasClass('disabled'))
				return;
			selectedEventListIndex--;
			updateNavigationTitle();
			calendar.fullCalendar('refetchEvents');
		});
		$('.nav-next .button').click(function(event) {
			event.preventDefault();
			if ($(this).hasClass('disabled'))
				return;
			selectedEventListIndex++;
			updateNavigationTitle();
			calendar.fullCalendar('refetchEvents');
		});

		var selectedCourses = [];
		$(document).on('click', '.course.alert-box .close', function(event) {
			var id = $(this).parents('.course').attr('id'),
				index = selectedCourses.indexOf(id);
			selectedCourses.splice(index, 1);
			if (selectedCourses.length == 0)
				$('#go').addClass('disabled');
		}).on('click', '.select-all', function(event) {
			event.preventDefault();
			toggleAll(this, true);
		}).on('click', '.deselect-all', function(event) {
			event.preventDefault();
			toggleAll(this, false);
		}).on('keydown', function(event) {
			console.log(event);
			var w = event.which || event.keyCode;
			if (w == $.ui.keyCode.LEFT) {
				$('.nav-prev .button').click();
			} else if (w == $.ui.keyCode.RIGHT) {
				$('.nav-next .button').click();
			}
		});

		$('#search-box').keydown(function(event) {
			var w = event.which || event.keyCode;
			if (w == $.ui.keyCode.ENTER)
			{
				$('#search-box').autocomplete('search', $('#search-box').val());
				event.preventDefault();
			}
		}).autocomplete({
			source: function(request, response) {
				$.ajax({
					url: '/search.json',
					dataType: 'json',
					data: {
						term: $("#term :checked").attr('name'),
						query: request.term
					},
					success: function(data) {
						response(data.results);
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
							.scrollintoview({
								complete: function() {
									setTimeout(function() {
										$sect.addClass('secondary');
									}, 500);
								}
							})
							.removeClass('secondary');
						
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
						var $section = $(html);
						$('#accordion').append($section);
						$section.scrollintoview();

						selectedCourses.push(ui.item.value);
						if (selectedCourses.length)
							$('#go').removeClass('disabled');

						$('#search-box').val('');
					}
				});
			}
		})
		.data('ui-autocomplete')._renderItem = function(ul, item) {
			return $('<li />')
				.append('<a><span class="title">'+item.title+'</span><br /><span class="subtitle">'+item.subtitle+'</span></a>')
				.appendTo(ul);
		};

		$('#search-button').click(function(event) {
			event.preventDefault();

			$('#search-box').autocomplete('search', $('#search-box').val());
		});

		$('#go').click(function(event) {
			event.preventDefault();

			function pad(num) {
				return num.toString().pad(2, "0");
			}
			function timeString(date) {
				return pad(date.getHours()) + ":" + pad(date.getMinutes());
			}

			var events = eventLists.busyTimes;
				checkboxes = $('form').serializeArray();

			if (checkboxes.length == 0)
				return;

			events = $.map(events, function(calendarEvent, i) {
				return calendarEvent.url ? null : [columbiaDays[calendarEvent.start.getDay()]+timeString(calendarEvent.start)+"-"+timeString(calendarEvent.end)];
			});

			checkboxes = $.map(checkboxes, function(element) {
				if (element.value == "on")
					return element.name;
				else
					return null;
			});

			$.ajax({
				url: '/events.json',
				dataType: 'json',
				data: {
					term: $("#term :checked").attr('name'),
					busyTimes: events,
					sections: checkboxes
				},
				success: function(data) {
					calendar.scrollintoview();
					selectedEventListIndex = 0;
					eventLists = data;
					calendar.fullCalendar('refetchEvents');
					updateNavigationTitle();
				}
			});
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

// http://jsfromhell.com/string/pad
//
// String.pad(length: Integer, [substring: String = " "], [type: Integer = 0]): String
// Returns the string with a substring padded on the left, right or both sides.
//
// length: amount of characters that the string must have
// substring: string that will be concatenated
// type: specifies the side where the concatenation will happen, where:
//		   0 = left, 1 = right and 2 = both sides

String.prototype.pad = function(l, s, t){
	return s || (s = " "), (l -= this.length) > 0 ? (s = new Array(Math.ceil(l / s.length)
		+ 1).join(s)).substr(0, t = !t ? l : t == 1 ? 0 : Math.ceil(l / 2))
		+ this + s.substr(0, l - t) : this;
};
