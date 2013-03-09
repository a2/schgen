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


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/search.json')
def search():
    term = request.args.get('term')
    course = request.args.get('course')
    title = request.args.get('title')
    description = request.args.get('description')
    
    if term and (bool(course) + bool(title) + bool(description) == 1):
        if course:
            results = make_api_query(term=term, course=course)
        elif title:
            results = make_api_query(term=term, title=title)
        elif description:
            results = make_api_query(term=term, description=description)

        if results['status_code'] != 200:
            print 'API server returned errors'
            abort(400)  # Bad request

        return jsonify({
            'results': results['data']
        })
    else:
        print 'Invalid parameters term=%s, course=%s, title=%s, description=%s' \
            % (term, course, title, description)
        abort(400)  # Bad request

@app.route('/courses.json')
def courses():
    term = request.args.get('term')
    courses = request.args.get('courses')
    
    if term and courses:
        courses = courses.split(',')
        results = {c: make_api_query(term=term, course=c) for c in courses if c}

        status_codes_OK = [v['status_code'] == 200 for v in results.values()]

        if not all(status_codes_OK):
            print 'API server returned errors'
            abort(400)  # Bad request

        data = {}
        for key in results.keys():
            data[key] = {course['Course']: course for course in results[key]['data']}

        {k: results[k]['data'] for k in results.keys()}

        return jsonify({
            'combinations': section_combinations(results),
            'course_data': data,
        })
    else:
        print 'Invalid parameters term=%s, courses=%s' % (term, courses)
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
