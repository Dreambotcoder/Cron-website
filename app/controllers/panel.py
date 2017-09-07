import requests
from flask import Blueprint, session, url_for, redirect, render_template, json, request, abort

from app.config import API_URL

panel_controller = Blueprint('panel_controller', __name__)


@panel_controller.route("/crondroid/panel/")
@panel_controller.route("/crondroid/panel")
def redirect_to_home():
    return redirect(url_for('panel_controller.land'))



@panel_controller.route("/crondroid/test")
def test():
    return render_template("panel/modals/bot_info.html")

@panel_controller.route("/crondroid/panel/home")
def land():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    post_dict = {
        "backend-token" : "fuck-me-hard-daddy"
    }
    response = requests.post(API_URL + "/api/backend/all_scripts", json=post_dict)
    script_data = json.loads(response.text)
    return render_template("panel/panel_home.html",
                           webToken=session['web_token'],
                           activeNav="home",
                           script_data=script_data['result'])


@panel_controller.route("/crondroid/panel/botlist")
def botlist():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))

    post_dict = {
        "web_token": session['web_token']
    }
    response = requests.post(API_URL + "/api/script_for_room", json=post_dict)
    script_data = json.loads(response.text)

    post_dict_2 = {
        "web_token" : session['web_token']
    }
    response_2 = requests.post(API_URL + "/api/bots/web",json=post_dict_2)
    botting_data = json.loads(response_2.text)

    print bot_data
    return render_template("panel/panel_list.html",
                           webToken=session['web_token'],
                           activeNav="botlist",
                           script_data=script_data,
                           botting_data=botting_data['bot_data'])


@panel_controller.route("/crondroid/panel/remote_control")
def remote_control():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    return render_template("panel/panel_remote.html", webToken=session['web_token'], activeNav="remote")


@panel_controller.route("/crondroid/panel/history")
def history():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    return render_template("panel/panel_history.html", webToken=session['web_token'], activeNav="bothistory")


@panel_controller.route("/crondroid/panel/settings")
def settings():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    return render_template("panel/panel_settings.html", webToken=session['web_token'], activeNav="settings")


@panel_controller.route('/crondroid/panel/bot-data', methods=['POST'])
def bot_data():
    if "web_token" not in session:
        return abort(400)
    web_token = session["web_token"]
    bot_id = request.json.get("bot_id")
    post_dict = {
        "web_token" : web_token,
        "bot_id" : bot_id
    }
    response = requests.post(API_URL + "/api/bots/specific", json=post_dict)
    bot_data = json.loads(response.text)
    return json.dumps(bot_data["bot_data"][0])


@panel_controller.route("/crondroid/panel/bot_modal", methods=["POST"])
def bot_modal():
    if "web_token" not in session:
        return abort(400)
    bot_id = request.json.get("bot_id")
    print bot_id
    return render_template("panel/bot_modal.html", bot_id=bot_id)