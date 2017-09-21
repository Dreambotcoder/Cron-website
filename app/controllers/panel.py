import os
from pprint import pprint

import requests
from flask import Blueprint, session, url_for, redirect, render_template, json, request, abort
from flask_socketio import emit

from app import get_root
from app.config import API_URL

panel_controller = Blueprint('panel_controller', __name__)


@panel_controller.route("/util/item", methods=["POST"])
def get_item_name():
    itemId = request.json.get("item_id")
    SITE_ROOT = get_root()
    uri = os.path.join(SITE_ROOT, "static/json", 'item_names.json')
    data = json.load(open(uri))
    try:
        item_name = data[str(itemId)]["name"]
    except KeyError as e:
        uri_ = os.path.join(SITE_ROOT, "static/json", 'nontradeables.json')
        data_ = json.load(open(uri_))
        try:
            item_name = data_[str(itemId)]["name"]
        except KeyError as e:
            item_name = ""
    return item_name


@panel_controller.route("/panel/inventory", methods=["POST"])
def inventory_loader():
    data = {}
    inventory_data = request.json.get("inventory_data")
    data["inventory_data"] = json.loads(inventory_data)
    print json.dumps(data)
    render_template("panel/modals/inventory.html", inventory=json.dumps(data))


@panel_controller.route("/emit", methods=["POST"])
def emit_stuff():
    bot_alias = request.json.get("bot_alias")
    web_token = request.json.get("web_token")
    bot_id = request.json.get("bot_id")
    ip_address = request.json.get("ip_address")
    clock_in = request.json.get("clock_in")
    user_room = 'user_{}'.format(web_token)
    emit('add_bot', json.dumps(
        {
            'name': bot_alias,
            "id": bot_id,
            "ip_address": ip_address,
            "clock_in": clock_in
        }
    ), room=user_room, namespace="")
    return "done"


@panel_controller.route('/emit/update', methods=["POST"])
def emit_bot():
    bot_id = request.json.get("bot_id")
    web_token = request.json.get("web_token")
    user_room = 'details_{}'.format(web_token + "_" + str(bot_id))
    emit('update_details', json.dumps(
        {
            "data": json.loads(json.dumps(request.json.get("data")))
        }
    ), room=user_room, namespace="")
    return ""


@panel_controller.route('/emit/remove', methods=["POST"])
def remove_bot():
    bot_id = request.json.get("bot_id")
    web_token = request.json.get("web_token")
    bot_name = request.json.get("bot_name")
    user_room = 'user_{}'.format(web_token)
    emit('remove_bot', json.dumps(
        {
            "id": bot_id,
            "name" : bot_name
        }
    ), room=user_room, namespace="")
    return ""


@panel_controller.route("/crondroid/entryload")
def entry_load():
    return render_template("panel/botlist_entry.html")


@panel_controller.route("/crondroid/panel/")
@panel_controller.route("/crondroid/panel")
def redirect_to_home():
    return redirect(url_for('panel_controller.land'))


@panel_controller.route("/crondroid/test/<int:bot_id>")
def test(bot_id):
    print bot_id
    return render_template("panel/modals/bot_info.html")


@panel_controller.route("/crondroid/panel/home")
def land():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    post_dict = {
        "backend-token": "fuck-me-hard-daddy"
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
        "web_token": session['web_token']
    }
    response_2 = requests.post(API_URL + "/api/bots/web", json=post_dict_2)
    botting_data = json.loads(response_2.text)
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
    return get_bot_data(request.json.get("bot_id"))


def get_bot_data(bot_id):
    if "web_token" not in session:
        return abort(400)
    web_token = session["web_token"]
    bot_id = request.json.get("bot_id")
    post_dict = {
        "web_token": web_token,
        "bot_id": bot_id
    }
    response = requests.post(API_URL + "/api/bots/specific", json=post_dict)
    bot_data = json.loads(response.text)
    return json.dumps(bot_data["bot_data"][0])


@panel_controller.route('/crondroid/panel/details')
def details(bot_id):
    pass


@panel_controller.route('/crondroid/panel/botview/', methods=["POST"])
def bot_view():
    bot_id = request.json.get("bot_id")
    data = json.loads(get_bot_data(bot_id))
    print json.dumps(data)
    if "web_token" not in session:
        return abort(400)
    return render_template("panel/botdetails.html", bot=data, webToken=session['web_token'], bot_id=bot_id)


@panel_controller.route("/crondroid/panel/bot_modal/", methods=["GET"])
def bot_modal(bot_id):
    if "web_token" not in session:
        return abort(400)
    return render_template("panel/bot_modal.html")
