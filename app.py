from flask import (Flask, request, url_for, jsonify, render_template, abort)
import os
import requests
from colorama import Fore, Back, Style, init
import itertools
import re
from time import strftime, strptime

app = Flask(__name__)

init(autoreset=True)

def replace_roman_numerals(string):
    return re.sub("(?i)\\bM{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\\b",
        lambda m: m.group(0).upper(), string)

def format_course_title(section):
    return replace_roman_numerals(section['CourseTitle'].title())

def make_api_query(**kwargs):
    url = 'http://data.adicu.com/courses'
    params = kwargs
    params['api_token'] = app.DATA_ADICU_COM_API_KEY
    
    print 'Making api query to %s' % url
    results = requests.get(url, params=params)
    return results.json()

def section_combinations(courses):
    sn = []
    for c, v in courses.iteritems():
        section_names = []
        for i in v['data']:
            section_names.append(i['Course'])
        sn.append(section_names)

    return list(itertools.product(*sn))


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/search.json')
def search():
    term = request.args.get('term')
    query = request.args.get('query')
    
    if term and query:
        query = re.sub("\\b([A-Za-z ]{4})([A-Za-z])([0-9 ]+)\\b", "\\1\\3\\2", query)

        data = []
        course_ids = []

        for criterion in ['course', 'title', 'description']:
            kwargs = {'term': term, criterion: query}
            results = make_api_query(**kwargs)

            if results['status_code'] != 200:
                continue

            for course in results['data']:
                course_id = re.sub("([A-Za-z ]+)([0-9 ]+)([A-Za-z])([0-9]+)",
                    "\\1\\3\\2", course['Course'])
                if course_id not in course_ids:
                    title = format_course_title(course)
                    description = course['Description']
                    if description and len(description) > app.COURSE_DESCRIPTION_MAX_LENGTH:
                        description = description[:app.COURSE_DESCRIPTION_MAX_LENGTH] + '&hellip;'

                    course_ids.append(course_id)
                    data.append({
                        'title': course_id + ' &bull; ' + title,
                        'subtitle': description,
                        'value': course_id
                    })
        
        return jsonify({
            'results': data
        })
    else:
        print 'Invalid parameters term=%s, query=%s' % (term, query)
        abort(400)  # Bad request

@app.route('/courses.json')
def courses():
    term = request.args.get('term')
    courses = request.args.get('courses')
    
    if term and courses:
        courses = courses.split(',')
        results = {c: make_api_query(term=term,
            course=re.sub("\\b([A-Za-z ]{4})([A-Za-z])([0-9 ]+)\\b",
            "\\1\\3\\2", c)) for c in courses if c}

        status_codes_OK = [v['status_code'] == 200 for v in results.values()]

        if not all(status_codes_OK):
            print 'API server returned errors'
            abort(400)  # Bad request

        data = {}
        for key in results.keys():
            data[key] = {course['Course']: course for course in results[key]['data']}

        return jsonify({
            'combinations': section_combinations(results),
            'course_data': data,
        })
    else:
        print 'Invalid parameters term=%s, courses=%s' % (term, courses)
        abort(400)  # Bad request

@app.route('/sections.html')
def sections():
    term = request.args.get('term')
    course = request.args.get('course')
    
    if term and course:
        course = re.sub("\\b([A-Za-z ]{4})([A-Za-z])([0-9 ]+)\\b", "\\1\\3\\2", course)
        results = make_api_query(term=term, course=course)

        if results['status_code'] != 200:
            print 'API server returned errors'
            abort(400)  # Bad request

        sections = []
        context = {'sections': sections}
        for section in results['data']:
            if 'course_id' not in context:
                course_id = re.sub("([A-Za-z ]+)([0-9 ]+)([A-Za-z])[0-9]+",
                    "\\1\\3\\2", section['Course'])
                context['course_id'] = course_id
                context['course_id_and_title'] = course_id + ' &bull; ' + \
                    format_course_title(section)

            data = {}
            data['id'] = int(re.sub("[A-Za-z ]+[0-9 ]+[A-Za-z]([0-9]+)",
                "\\1", section['Course']))
            data['full_id'] = section['Course']
            
            professors = []
            for i in range(1, 5):
                instructor_key = 'Instructor' + str(i) + 'Name'
                if instructor_key in section and section[instructor_key]:
                    professor = section[instructor_key]
                    professor = ' '.join(reversed(professor.split(', '))).title()
                    professors.append(professor)

            data['professors'] = ", ".join(professors)

            meetings = []
            for i in range(1, 7):
                meetsOn_key = 'MeetsOn' + str(i)
                if meetsOn_key in section and section[meetsOn_key]:
                    start = strftime("%I:%M %p",
                        strptime(section['StartTime' + str(i)], "%H:%M:%S"))
                    if start[0] == '0':
                        start = start[1:]

                    end = strftime("%I:%M %p",
                        strptime(section['EndTime' + str(i)], "%H:%M:%S"))
                    if end[0] == '0':
                        end = end[1:]

                    meetings.append({
                        'meetsOn': section[meetsOn_key],
                        'startTime': start,
                        'endTime': end
                    })

            data['meetings'] = meetings

            sections.append(data)

        sections.sort(key=lambda section: section['id'])

        return render_template('sections.html', **context)
    else:
        print 'Invalid parameters term=%s, course=%s' % (term, course)
        abort(400)  # Bad request

if __name__ == '__main__':
    app.COLUMBIA_DAYS = "UMTWRFS"
    app.COLUMBIA_DAYS_DICT = {
        "U": "Sunday",
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "R": "Thursday",
        "F": "Friday",
        "S": "Saturday"
    }
    app.COURSE_DESCRIPTION_MAX_LENGTH = 600
    app.DATA_ADICU_COM_API_KEY = os.environ.get('DATA_ADICU_COM_API_KEY')

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('DEBUG'):
        print Fore.RED, 'Running in DEBUG mode!'
        app.debug = True

    app.run(host='0.0.0.0', port=port)
