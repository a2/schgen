import os
from flask import (Flask, request, render_template, url_for, g, jsonify,
                   redirect, abort, make_response)

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    url_for('static', filename='css/default.css')
    url_for('static', filename='css/normalize.css')
    url_for('static', filename='css/normalize.min.css')
