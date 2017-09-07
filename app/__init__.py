from flask import Flask, redirect, url_for, render_template

from app.controllers.login import login_controller
from app.controllers.panel import panel_controller
from app.controllers.website import website_controller

app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.secret_key = "i-am-the-one-who-knocks"

app.register_blueprint(login_controller)
app.register_blueprint(panel_controller)
app.register_blueprint(website_controller)


@app.context_processor
def active_nav():
    def _active_nav(id, active_id):
        if id == active_id:
            return "active-nav-tab"
        return ""
    return dict(active_nav=_active_nav)


@app.errorhandler(500)
def page_not_found(e):
    return render_template('misc/500_error.html'), 500


if __name__ == '__main__':
    app.run()
