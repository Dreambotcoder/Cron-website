import requests
from flask import Blueprint, render_template, request, abort, session, redirect, url_for

from app.config import API_URL

login_controller = Blueprint('login_controller', __name__)


@login_controller.route("/crondroid/log", methods=["GET"])
def test():
    return render_template("test.html")


@login_controller.route("/crondroid/remote/<int:remote_id>", methods=["GET"])
def remote(remote_id):
    return render_template("remote.html", bot_id=remote_id)


@login_controller.route("/crondroid/login/auth", methods=['POST'])
def auth():
    data = request.form
    web_token = data['web_token']
    token_pass = data['token_pass']
    if web_token is None or token_pass is None:
        return abort(400)
    post_dict = {
        "web_token": web_token,
        "token_pass": token_pass
    }
    response = requests.post(API_URL + "/api/authenticate", json=post_dict)
    if response.status_code == 200:
        session['web_token'] = web_token
        session['script_id'] = response.text
        return url_for("panel_controller.land")
    else:
        abort(400)


@login_controller.route("/crondroid/logout")
def logout():
    session.pop('web_token', None)
    return redirect(url_for("login_controller.land"))


@login_controller.route("/crondroid")
@login_controller.route('/crondroid/login')
def land():
    return render_template("login/login-lander.html")
