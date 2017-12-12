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

from apiclient import discovery
from oauth2client.contrib.flask_util import UserOAuth2


# Set up application
app = Flask(__name__)

FLASK_SESSION_SECRET = secret_key.SECRET_KEY
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'

app.config['SECRET_KEY'] = FLASK_SESSION_SECRET
app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_FILE'] = CLIENT_SECRET_FILE


oauth2 = UserOAuth2(app)


class Dish:
    def __init__(self, list_dish):
        self.dish_name = list_dish[3]
        self.prices = [list_dish[i] for i in range(4, len(list_dish) - 4)]


class MenuCategory:
    def __init__(self, first_dish):
        self.content_id = first_dish[0]
        self.category_id = first_dish[1]
        self.category_name = first_dish[2]
        self.section_id = "content-" + self.content_id
        self.carousel_id = "carousel-" + self.category_id
        self.carousel_title = self.category_name + " photo carousel"
        self.img_url = "background-image: url(" \
                       "'static/img/menuphoto/carousel-" + self.category_id \
                       + "-1.jpg');"
        self.dishes = []
        self.dishes.append(Dish(first_dish))
        self.dishes_col1 = []
        self.dishes_col2 = []

    def add_dish(self, list_dish):
        self.dishes.append(Dish(list_dish))

    def divide_group(self):
        for i in range(int(len(self.dishes) / 2) + 1):
            self.dishes_col1.append(self.dishes[i])
        for i in range(int(len(self.dishes) / 2) + 1, len(self.dishes)):
            self.dishes_col2.append(self.dishes[i])


def get_menu_info(http=None, credentials=None):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno/edit
    """

    http = oauth2.http()

    service = discovery.build('sheets', 'v4')

    spreadsheet_id = '1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno'
    range_name = 'menu!A2:G'

    # Call the service using the authorized Http object.
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name)
    response = request.execute(http=http)
    values = response.get('values', [])

    categories = {}

    if not values:
        logging.exception('Google spreadsheet read fails.')
        # TODO: Read cached page
    else:
        for row in values:
            if row[0] in categories:
                categories[row[0]].add_dish(row)
            else:
                categories[row[0]] = MenuCategory(row)
    for category in categories:
        logging.log(category.content_id)
    # TODO: Cache page

    return categories


@app.route('/')
@app.route('/index.html')
@app.route('/index')
@app.route('/home')
def home():
    return render_template('index-dynamic.html')


@app.route('/menu')
@app.route('/menu.html')
def menu():
    return render_template('menu.html')


@app.route('/newmenu')
@app.route('/newmenu.html')
@oauth2.required(scopes=[SCOPES])
def new_menu():
    menu = get_menu_info()
    return render_template('menu-dynamic.html', menu=menu)


# @app.route(api_auth.callback_path)
# def oauth_callback():
#     return api_auth.callback_handler()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index-dynamic.html')


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
