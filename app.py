from flask import (Flask, request, url_for, jsonify, render_template, abort)
import os
import requests

app = Flask(__name__)


def make_api_query(term, course):
    url = 'http://data.adicu.com/courses'
    params = {
        'api_token': app.DATA_ADICU_COM_API_KEY,
        'term': term,
        'course': course
    }
    results = requests.get(url, params=params)
    return results.json()


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/courses.json')
def courses():
    term = request.args.get('term')
    course = request.args.get('course')
    results = make_api_query(term, course)
    if term and course:
        return jsonify(results)
    else:
        abort(400)  # Bad request

if __name__ == '__main__':

    app.DATA_ADICU_COM_API_KEY = os.environ.get('DATA_ADICU_COM_API_KEY')

    #  Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('DEBUG'):
        app.debug = True

    app.run(host='0.0.0.0', port=port)

    url_for('static', filename='css/default.css')
    url_for('static', filename='css/normalize.css')
    url_for('static', filename='css/normalize.min.css')
