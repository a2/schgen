from flask import (Flask, request, url_for, jsonify, render_template, abort)
import os
import requests
from colorama import Fore, Back, Style, init
import itertools
import datetime
import time


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


def parse_meeting_times(MeetsOn1, StartTime1, EndTime1,
                        MeetsOn2=None, StartTime2=None, EndTime2=None):
    '''
    Transform the course times to
    [
        (start_datetime1, end_datetime1),
        (start_datetime2, end_datetime2),
    ]
    '''

    days = 'UMTWRFS'

    mt = []

    for day in MeetsOn1:
        st = time.strptime(StartTime1, '%H:%M:%S')
        sdt = datetime.datetime(
            year=1970,
            month=1,
            day=4 + days.index(day),
            hour=st[3],
            minute=st[4],
            second=st[5],
        )

        et = time.strptime(EndTime1, '%H:%M:%S')
        edt = datetime.datetime(
            year=1970,
            month=1,
            day=4 + days.index(day),
            hour=et[3],
            minute=et[4],
            second=et[5],
        )

        mt.append((sdt, edt))

    if MeetsOn2:
        for day in MeetsOn2:
            st = time.strptime(StartTime2, '%H:%M:%S')
            sdt = datetime.datetime(
                year=1970,
                month=1,
                day=4 + days.index(day),
                hour=st[3],
                minute=st[4],
                second=st[5],
            )

            et = time.strptime(EndTime2, '%H:%M:%S')
            edt = datetime.datetime(
                year=1970,
                month=1,
                day=4 + days.index(day),
                hour=et[3],
                minute=et[4],
                second=et[5],
            )

            mt.append((sdt, edt))

    return mt


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
