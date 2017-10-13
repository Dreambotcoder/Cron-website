import os
from pprint import pprint

import requests
from flask import Blueprint, session, url_for, redirect, render_template, json, request, abort
from flask_socketio import emit

from app import get_root, xp_to_lvl_calc
from app.config import API_URL, SKILLS

panel_controller = Blueprint('panel_controller', __name__)


@panel_controller.route('/crondroid/panel/logview', methods=["POST"])
def log_view():
    return render_template('panel/modals/log_modal.html')



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


@panel_controller.route('/emit/remote/process', methods=["POST"])
def emit_remote_process():
    web_token = request.json.get("web_token")
    bot_name = request.json.get("bot_name")
    bot_id = request.json.get("bot_id")
    percentage = request.json.get("percentage")
    message = request.json.get("message")
    user_room = 'remote_{}'.format(web_token)
    emit('update_process', json.dumps(
        {
            "name": str(bot_name),
            "id": int(bot_id),
            "percentage": int(percentage),
            "message": str(message)
        }
    ), room=user_room, namespace="")
    return ""


@panel_controller.route('/emit/panel/notification', methods=['POST'])
def emit_notification():
    web_token = request.json.get("web_token")
    bot_id = request.json.get("bot_id")
    title = request.json.get("title")
    text = request.json.get("text")
    timestamp = request.json.get("timestamp")
    user_room = 'details_{}'.format(web_token + "_" + str(bot_id))
    emit('add_shout', json.dumps(
        {
            "title": title,
            "text": text,
            "timestamp": timestamp
        }
    ), room=user_room, namespace="")
    return ""


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
    xp_data = {}
    stat_data = json.loads(request.json.get('stat_data'))
    for skill in SKILLS:
        level = xp_to_lvl_calc(int(stat_data.get(str(skill)).get("current_xp")))
        xp_data[str(skill)] = {"level": int(level)}
    emit('update_details', json.dumps(
        {
            "data": json.loads(request.json.get("data")),
            "stat_data": xp_data
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
            "name": bot_name
        }
    ), room=user_room, namespace="")
    return ""


@panel_controller.route("/crondroid/panel")
def redirect_to_home():
    return redirect(url_for('panel_controller.land'))


@panel_controller.route("/crondroid/panel/home")
def land():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    post_dict = {
        "backend-token": "fuck-me-hard-daddy",
        "web_token": session["web_token"]
    }
    response = requests.post(API_URL + "/api/backend/all_scripts", json=post_dict)
    script_data = json.loads(response.text)

    announcements = requests.get(API_URL + "/api/announcements")
    announcement_data = json.loads(announcements.text)
    current_script = {}
    for script in script_data['result']:
        if script["script_id"] == int(session["script_id"]):
            current_script = script
    return render_template("panel/panel_home.html",
                           webToken=session['web_token'],
                           activeNav="home",
                           script_data=script_data['result'],
                           bot_count=script_data['bot_count'],
                           current_script=current_script, announcements=announcement_data)


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
    post_dict = {
        "script_id": int(session['script_id'])
    }
    post_dict_2 = {
        "web_token": session["web_token"],
        "script_id": int(session["script_id"])
    }
    response = requests.post(API_URL + "/api/remote", json=post_dict)
    commands_dict = json.loads(response.text)
    bots_request = requests.post(API_URL + "/api/bots/web/format/remote", json=post_dict_2)
    bot_dict = json.loads(bots_request.text)
    return render_template("panel/panel_remote.html",
                           webToken=session['web_token'],
                           activeNav="remote",
                           commands=commands_dict,
                           available_bots=bot_dict["available"],
                           processing_bots=bot_dict["processing"],
                           polling_bots=bot_dict['polling'])


@panel_controller.route("/crondroid/panel/history")
def history():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    history_dict = {
        "web_token": str(session['web_token']),
        "backend_token": "fuck-me-hard-daddy"
    }
    response = requests.post(API_URL + "/api/logs", json=history_dict)
    print response.text
    history_data = json.loads(response.text)
    return render_template("panel/panel_history.html",
                           webToken=session['web_token'],
                           activeNav="bothistory",
                           timeline=history_data['timeline_data'])


@panel_controller.route("/crondroid/panel/settings")
def settings():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    return render_template("panel/panel_settings.html", webToken=session['web_token'], activeNav="settings")


@panel_controller.route("/crondroid/panel/loader/snapshot", methods=["POST"])
def snapshot_loader():
    session_id = request.json.get("bot_id")
    snapshot_id = request.json.get("snapshot_id")
    snapshot_dict = {
        "bot_id" : session_id,
        "snapshot_id" : snapshot_id,
        "backend_token" : "fuck-me-hard-daddy"
    }
    response = requests.post(API_URL + "/api/snapshots/specific/base64", json=snapshot_dict)
    base64_source = response.text
    return base64_source


@panel_controller.route('/crondroid/panel/bot-data', methods=['POST'])
def bot_data():
    return get_bot_data(request.json.get("bot_id"))


@panel_controller.route('/crondroid/panel/levels', methods=["POST"])
def get_levels():
    if "web_token" not in session:
        return abort(401)
    bot_id = request.json.get("bot_id")
    level_dict = {
        "bot_id": bot_id,
        "web_token": session["web_token"],
        "backend_token" : "fuck-me-hard-daddy"
    }
    response = requests.post(API_URL + "/api/skills/levels", json=level_dict)
    bot_data = json.loads(response.text)
    xp_data = {}
    xp_data["stat_data"] = xp_data
    print "WHOA"
    pprint(xp_data)
    print json.dumps(bot_data)
    return json.dumps(bot_data)


def get_bot_data(bot_id):
    if "web_token" not in session:
        return abort(400)
    web_token = session["web_token"]
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


@panel_controller.route('/crondroid/panel/graphs')
def graph_view():
    if "web_token" not in session:
        return redirect(url_for("login_controller.land"))
    return render_template("panel/panel_graph.html",
                           webToken=session['web_token'],
                           activeNav="graphing")


@panel_controller.route('/crondroid/panel/botview/', methods=["POST"])
def bot_view():
    bot_id = request.form["bot_id"]
    data = json.loads(get_bot_data(bot_id))

    print json.dumps(data)
    if "web_token" not in session:
        return abort(400)
    return render_template("panel/botdetails.html",
                           bot=data,
                           webToken=session['web_token'],
                           bot_id=bot_id,
                           skills=SKILLS,
                           stat_data=data["stat_data"],
                           snapshots=data["snapshots"])
