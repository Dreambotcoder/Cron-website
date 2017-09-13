from flask import Blueprint, render_template

website_controller = Blueprint('website_controller', __name__)


@website_controller.route('/')
def index():
    return render_template('website/lander_index.html')


@website_controller.route('/about')
def info():
    return render_template('website/about_us.html')


@website_controller.route('/test')
def test():
    return render_template('test.html')


@website_controller.route('/contact')
def contact():
    return render_template('website/contact_us.html')


