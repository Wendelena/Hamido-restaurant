#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# [START app]
from __future__ import print_function

import logging

from flask import Flask, render_template
import secret_key

import gae_api_utils
from hamido_menu import get_menu_info


# Local environment: True; GAE: False
gae_api_utils.LOCAL = False


# Set up application
app = Flask(__name__)

FLASK_SESSION_SECRET = secret_key.SECRET_KEY
SCOPES = gae_api_utils.SCOPES
CLIENT_SECRET_FILE = gae_api_utils.CLIENT_SECRET_FILE

app.config['SECRET_KEY'] = FLASK_SESSION_SECRET
app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_FILE'] = CLIENT_SECRET_FILE


oauth2 = gae_api_utils.oauth_setup(app)


@app.route('/')
@app.route('/index.html')
@app.route('/index')
@app.route('/home')
def home_page():
    return render_template('index-dynamic.html')


@app.route('/menu')
@app.route('/menu.html')
def menu_page():
    menu = get_menu_info()
    return render_template('menu-dynamic.html', menu=menu)


@app.route('/newmenu')
@app.route('/newmenu.html')
@oauth2.required(scopes=[SCOPES])
def new_menu_init():
    menu = get_menu_info(cached=False)
    return render_template('menu-dynamic.html', menu=menu)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index-dynamic.html')


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
