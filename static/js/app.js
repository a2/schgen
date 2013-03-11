;(function ($, window, undefined) {
	$(function() {
		$(document).foundation();
		var columbiaDays = "UMTWRFS";

		var calendar = $('#calendar'),
			calendarEvents = [];
		calendar.fullCalendar({
			events: function(start, end, callback) {
				function pad(num) {
					return num.toString().pad(2, "0");
				}
				function timeString(date) {
					return pad(date.getHours()) + escape("%3A") + pad(date.getMinutes());
				}

				var events = calendarEvents;
					checkboxes = $('form').serializeArray();

				console.log(events, checkboxes);
				if (!(events.length && checkboxes.length))
					return;

				events = $.map(events, function(event, i) {
					return event.url ? null : [columbiaDays[event.start.getDay()]+timeString(event.start)+"-"+timeString(event.end)];
				}).join(',');

				checkboxes = $.map(checkboxes, function(element) {
					if (element.value == "on")
						return element.name;
					else
						return null;
				}).join(',');
								
				$.ajax({
					url: '/events.json',
					dataType: 'json',
					data: {
						term: $("#term :checked").attr('name'),
						busyTimes: events,
						checkboxes: checkboxes
					},
					success: function(data) {
						callback(data);
					}
				});
			},
			defaultView: 'agendaWeek',
			header: null,
			columnFormat: { agendaWeek: 'ddd' },
			allDaySlot: false,
			year: 2013,
			month: 2,
			date: 3,
			minTime: '8:00am',
			maxTime: '10:00pm',
			allDayDefault: false,
			editable: true,
			selectable: true,
			selectHelper: true,
			contentHeight: 1500,
			eventBackgroundColor: '#CC3D3D',
			select: function(start, end, allDay) {
				var event = {
					title: "Unavailable",
					start: start,
					end: end,
					allDay: allDay
				};
				calendarEvents.push(event);
				calendar
					.fullCalendar('renderEvent', event, false)
					.fullCalendar('unselect');
			},
			eventClick: function(calendarEvent) {
				if (calendarEvent.url) {
					window.open(event.url);r
					return false;
				}

				var index = calendarEvents.indexOf(calendarEvent);
				calendarEvents.splice(index, 1);

				calendar.fullCalendar('removeEvents',
					calendarEvent.id || calendarEvent._id);
			},
			eventDrop: function(calendarEvent, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, ui, view ) {
				var start = calendarEvent.start,
					end = calendarEvent.end;

				function trimStart() {
					console.log('Trim start');
					start = new Date(end.getTime());
					start.setHours(8);
					start.setMinutes(0);

					calendarEvent.start = start;
					calendar.fullCalendar('updateEvent', calendarEvent);
				}

				function trimEnd() {
					console.log('Trim end');
					end = new Date(start.getTime());
					end.setHours(22);
					end.setMinutes(0);
					
					calendarEvent.end = end;
					calendar.fullCalendar('updateEvent', calendarEvent);
				}

				if (start.getDay() != end.getDay()) {
					console.log('Different days');
					if (minuteDelta > 0) {
						trimEnd();
					} else {
						trimStart()
					}
				}
				else if (start.getHours() < 8)
					trimStart();
				else if (end.getHours() > 22 || (end.getHours == 22 && end.getMinutes() > 0))
					trimEnd();
				console.log(calendarEvent, dayDelta, minuteDelta, allDay);
			},
			eventResize: function(calendarEvent, dayDelta, minuteDelta, revertFunc, jsEvent, ui, view) {
				// console.log(calendarEvent, dayDelta, minuteDelta);
			}
		});

		var selectedCourses = [];
		$(document).on('click', '.course.alert-box .close', function(event) {
			var id = $(this).parents('.course').attr('id'),
				index = selectedCourses.indexOf(id);
			selectedCourses.splice(index, 1);
		});
		$('#search-box').keydown(function(event) {
			if (event.which == $.ui.keyCode.ENTER)
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
						console.log(data);
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
						$('#search-box').val('');
					}
				})
			}
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

		$('#go').click(function(event) {
			calendar.fullCalendar('refetchEvents');
			event.preventDefault();
		})
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
//           0 = left, 1 = right and 2 = both sides

String.prototype.pad = function(l, s, t){
    return s || (s = " "), (l -= this.length) > 0 ? (s = new Array(Math.ceil(l / s.length)
        + 1).join(s)).substr(0, t = !t ? l : t == 1 ? 0 : Math.ceil(l / 2))
        + this + s.substr(0, l - t) : this;
};
