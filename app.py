import flask
from recycle import recycle

app = flask.Flask(__name__)


@app.route('/')
def hello():
    return flask.render_template('index.html')


@app.route("/recycle/", methods=['POST'])
def perform_recycle():
    recycle()
    return flask.redirect('/')
