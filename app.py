from flask import Flask, request, redirect
import toml
data = toml.load("config.toml")


app = Flask(__name__)


@app.route("/auth")
def auth():
    return redirect(data["oauth2Providers"]["spotify"]["auth_uri"])

@app.route("/auth/callback")
def callback():
    code = request.args.get("code")


# @app.route('/login/spotify')
# def login_spotify():
