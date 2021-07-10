import flask
import spotipy
import config
import time
from recycle import recycle

app = flask.Flask(__name__)

app.secret_key = config.SECRET_KEY

scope = 'playlist-modify-public'


# Authorization step 1
@app.route('/')
def hello():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        scope=scope,
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=config.SPOTIPY_REDIRECT_URI)
    auth_url = sp_oauth.get_authorize_url()
    return flask.redirect(auth_url)


# Authorization step 2
@app.route("/callback")
def api_callback():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        scope=scope,
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=config.SPOTIPY_REDIRECT_URI)
    flask.session.clear()
    code = flask.request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    flask.session['token_info'] = token_info
    return flask.redirect('index')


@app.route('/index/')
def index():
    return flask.render_template('index.html')


@app.route("/recycle/", methods=['POST'])
def perform_recycle():
    flask.session['token_info'], authorized = get_token(flask.session)
    flask.session.modified = True
    if not authorized:
        return flask.redirect('/')
    sp = spotipy.Spotify(auth=flask.session.get('token_info').get('access_token'))
    recycle(sp)
    return flask.redirect('/index/')


def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            scope=scope,
            client_id=config.SPOTIPY_CLIENT_ID,
            client_secret=config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=config.SPOTIPY_REDIRECT_URI)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid



