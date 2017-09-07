from flask import Blueprint, render_template

website_controller = Blueprint('website_controller', __name__)


@website_controller.route('/')
def index():
    print 'INDEX ASKED'
    return render_template('website/lander_index.html')


@website_controller.route('/about')
def info():
    print 'ABOUT US'
    return render_template('website/about_us.html')


@website_controller.route('/contact')
def contact():
    print 'CONTACT'
    return render_template('website/contact_us.html')


