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

		function calendarEventDidUpdate(calendarEvent, minuteDelta) {
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
		}

		calendar.fullCalendar({
			events: function(start, end, callback) {
				if (eventLists.eventLists && selectedEventListIndex < eventLists.eventLists.length)
					callback(eventLists.eventLists[selectedEventListIndex]);
				else
					callback([]);
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
			eventBackgroundColor: '#fff',
			eventBorderColor: '#E6E6E6',
			select: function(start, end, allDay) {
				calendar.fullCalendar('renderEvent', {
					title: "Unavailable",
					start: start,
					end: end,
					allDay: allDay,
					backgroundColor: '#fff',
					borderColor: '#E6E6E6',
					textColor: '#000'
				}, false).fullCalendar('unselect');

				updateBusyTimes();
			},
			eventClick: function(calendarEvent) {
				if (calendarEvent.url) {
					window.open(calendarEvent.url);
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
				calendarEventDidUpdate(calendarEvent, minuteDelta);
				updateBusyTimes();
			},
			eventResize: function(calendarEvent, dayDelta, minuteDelta, revertFunc, jsEvent, ui, view) {
				calendarEventDidUpdate(calendarEvent, minuteDelta);
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

		var hasSearched = false;
		function updateNavigationTitle() {
			var length = eventLists.eventLists ? eventLists.eventLists.length : 0,
				prev = $('.nav-prev .button'),
				next = $('.nav-next .button');

			if (length == 0) {
				$('.nav-title').text("No Schedules");
				if (hasSearched) $('#no-schedules-alert-container').removeClass('hide');
			} else {
				$('.nav-title').text("Schedule " + (selectedEventListIndex + 1) + " / " + length);
				$('#no-schedules-alert-container').addClass('hide');
			}
			
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
			{
				eventLists = {busyTimes: []};
				calendar.fullCalendar('refetchEvents');
				
				$('#go').addClass('disabled');
			}
		}).on('click', '.select-all', function(event) {
			event.preventDefault();
			toggleAll(this, true);
		}).on('click', '.deselect-all', function(event) {
			event.preventDefault();
			toggleAll(this, false);
		}).on('keydown', function(event) {
			if ($(':focus').length)
				return;

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
						$('#accordion').append(html);
						var $go = $('#go').scrollintoview();

						selectedCourses.push(ui.item.value);
						if (selectedCourses.length)
							$go.removeClass('disabled');

						$('#search-box').val('');
					}
				});
			}
		})
		.data('ui-autocomplete')._renderItem = function(ul, item) {
			return $('<li />')
				.append('<a><span class="title">'+item.title+'</span><br />'+(item.subtitle?('<span class="subtitle">'+item.subtitle+'</span>'):'')+'</a>')
				.appendTo(ul);
		};

		$('#search-button').click(function(event) {
			event.preventDefault();

			$('#search-box').autocomplete('search', $('#search-box').val());
		});

		$('#go').click(function(event) {
			event.preventDefault();

			function pad(num) {
				return ((num < 10) ? "0" : "") + num;
			}
			function timeString(date) {
				return pad(date.getHours()) + ":" + pad(date.getMinutes());
			}

			var events = eventLists.busyTimes;
				checkboxes = $('form').serializeArray();

			if (checkboxes.length == 0)
				return;

			events = $.map(events, function(calendarEvent, i) {
				var start = new Date(calendarEvent.start),
					end = new Date(calendarEvent.end);
				return calendarEvent.url ? null : [columbiaDays[start.getDay()]+timeString(start)+"-"+timeString(end)];
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
					sections: checkboxes,
					courses: selectedCourses
				},
				success: function(data) {
					$('.navigation').scrollintoview();
					
					hasSearched = true;
					selectedEventListIndex = 0;
					eventLists = data;
					calendar.fullCalendar('refetchEvents');
					updateNavigationTitle();
				}
			});
		});
	});
})(jQuery, this);