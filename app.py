from flask import (Flask, request, url_for, jsonify, render_template, abort)
import os
import requests
from colorama import Fore, Back, Style, init
import itertools

app = Flask(__name__)

init(autoreset=True)


def make_api_query(term, course):
    url = 'http://data.adicu.com/courses'
    params = {
        'api_token': app.DATA_ADICU_COM_API_KEY,
        'term': term,
        'course': course
    }
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


@app.route('/courses.json')
def courses():
    term = request.args.get('term')
    courses = request.args.get('courses')

    if term and courses:
        courses = courses.split(',')
        results = {c: make_api_query(term, c) for c in courses if c}

        status_codes_OK = [v['status_code'] == 200 for v in results.values()]

        if not all(status_codes_OK):
            abort(400)  # Bad request

        return jsonify({
            'combinations': section_combinations(results),
            'course_data': results,
        })
    else:
        abort(400)  # Bad request

if __name__ == '__main__':

    app.DATA_ADICU_COM_API_KEY = os.environ.get('DATA_ADICU_COM_API_KEY')

    #  Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('DEBUG'):
        print Fore.RED, 'Running in DEBUG mode!'
        app.debug = True

    app.run(host='0.0.0.0', port=port)

    url_for('static', filename='css/default.css')
    url_for('static', filename='css/normalize.css')
    url_for('static', filename='css/normalize.min.css')
