import os
from pprint import pprint

import time
from flask import Flask, redirect, url_for, render_template, json, session, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)

# SOCKET-IO
socketio = SocketIO(app)


from app.controllers.login import login_controller
from app.controllers.panel import panel_controller
from app.controllers.website import website_controller

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.secret_key = "i-am-the-one-who-knocks"

app.register_blueprint(login_controller)
app.register_blueprint(panel_controller)
app.register_blueprint(website_controller)

botlist_clients = []


@app.context_processor
def active_nav():
    def _active_nav(id, active_id):
        if id == active_id:
            return "active-nav-tab"
        return ""

    return dict(active_nav=_active_nav)


@app.context_processor
def item_image():
    def _item_image(item_id):
        return "http://cdn.rsbuddy.com/items/" + str(item_id)

    return dict(item_image=_item_image)


@app.context_processor
def parse_value():
    def _parse_value(value):
        if "%" in value:
            return '<div class="progress"><div class="progress-bar" role="progressbar" ' \
                   'aria-valuenow="70"aria-valuemin="0" aria-valuemax="100" style="width:70%">70%</div></div> '
        else:
            return value

    return dict(parse_value=_parse_value)


@app.context_processor
def item_name():
    def _item_name(item_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        uri = os.path.join(SITE_ROOT, "static/json", 'item_names.json')
        data = json.load(open(uri))
        try:
            item_name = data[str(item_id)]["name"]
        except KeyError as e:
            return ""
        return item_name

    return dict(item_name=_item_name)


@app.context_processor
def parse_item_amount():
    def _parse_item_amount(amount):
        if int(amount) > 1000000:
            return str(int(float(amount) / float(1000000))) + "M"
        else:
            return amount

    return dict(parse_item_amount=_parse_item_amount)


@app.errorhandler(500)
def page_not_found(e):
    return render_template('misc/500_error.html'), 500


@socketio.on('auth')
def handle_message(data):
    if "web_token" in session and session["web_token"] == data['data']:
        user_room = 'user_{}'.format(session['web_token'])
        join_room(user_room)




if __name__ == '__main__':
    socketio.run(app, debug=True)
