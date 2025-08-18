import time

from flask import Blueprint, current_app, g

main = Blueprint('main', __name__)


@main.before_app_request
def before_request():
    g.t = time.time()


@main.get('/')
def index():
    return current_app.send_static_file('index.html')


@main.after_app_request
def after_request(response):
    current_app.logger.info('total time for request %s' % (time.time() - g.t))
    return response
