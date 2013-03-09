from flask import (Flask, request, url_for, jsonify, render_template, abort)
import os
import requests
from colorama import Fore, Back, Style, init
import itertools

app = Flask(__name__)

init(autoreset=True)


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


def search(term, course='', title='', description=''):
    """Searches for courses during a given term based on course ID, title,
    or description.

    Args:
        term (str): The term to search in.

    Kwargs:
        course (str): The course ID to search for.
        title (str): The title of the course to search for.
        description (str): The description of the course to search for.

    Returns:
        dict. The course data:
            {
                'results': [
                    {...},
                    {...},
                    ...
                ]
            }

    """
    if term and (course or title or description):
        kwargs = {'term': term}
        if course:
            kwargs['course'] = course
        if title:
            kwargs['title'] = title
        if description:
            kwargs['description'] = description

        results = make_api_query(**kwargs)
        
        if results['status_code'] != 200:
            print 'API server returned errors'
            return {}

        return {'results':results['data']}
    else:
        print 'Invalid parameters term=%s, course=%s, title=%s, description=%s' \
            % (term, course, title, description)
        return {}


def get_courses(term, courses):
    """Retrieve course data for courses during a given term.

    Args:
        term (str): The term to search in.
        courses (iterable): The courses to search for.
    
    Returns:
        dict. The course data::
            {
                "combinations": [...],
                "course_data": {
                        "ENGL1010": {
                                "ENGL1010C029": {...},
                                "ENGL1010C028": {...},
                                ...
                        },
                        "MATH1202": {
                                "MATH1202V005": {...},
                                "MATH1202V004", {...},
                                ...
                        },
                        ...
                }
            }

    """
    if term and len(courses):
        results = {c: make_api_query(term=term, course=c) for c in courses if c}

        status_codes_OK = [v['status_code'] == 200 for v in results.values()]

        if not all(status_codes_OK):
            print 'API server returned errors'
            return {}

        data = {}
        for key in results.keys():
            data[key] = {course['Course']: course for course in results[key]['data']}

        return {
            'combinations': section_combinations(results),
            'course_data': data,
        }
    else:
        print 'Invalid parameters term=%s, courses=%s' % (term, courses)
        return {}


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/search.json')
def search_json():
    term = request.args.get('term')
    course = request.args.get('course')
    title = request.args.get('title')
    description = request.args.get('description')
    
    results = search(term, course, title, description)

    if len(results):
        return jsonify(results)
    else:
        abort(400)  # Bad request

@app.route('/courses.json')
def courses_json():
    term = request.args.get('term')
    courses = request.args.get('courses').split(',')
    
    results = get_courses(term, courses)

    if len(results):
        return jsonify(results)
    else:
        abort(400)  # Bad request


if __name__ == '__main__':
    app.COLUMBIA_DAYS = "UMTWRFS"
    app.DATA_ADICU_COM_API_KEY = os.environ.get('DATA_ADICU_COM_API_KEY')

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('DEBUG'):
        print Fore.RED, 'Running in DEBUG mode!'
        app.debug = True

    app.run(host='0.0.0.0', port=port)

    url_for('static', filename='css/default.css')
    url_for('static', filename='css/normalize.css')
    url_for('static', filename='css/normalize.min.css')
