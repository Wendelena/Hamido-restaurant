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

import httplib2
import os

from apiclient import discovery
from oauth2client.client import GoogleCredentials
from oauth2client.contrib.appengine import OAuth2DecoratorFromClientSecrets
from oauth2client.contrib.flask_util import UserOAuth2
# from oauth2client import client
# from oauth2client import tools
# from oauth2client.file import Storage

import pickle
from google.appengine.api import memcache
from google.appengine.api import users
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.appengine import StorageByKeyName


DEFAULT_CREDENTIALS = GoogleCredentials.get_application_default()


# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
# CLIENT_SECRET_FILE = 'client_secret.json'
# APPLICATION_NAME = 'Google Sheets API Python Quickstart'


# def get_credentials():
#     """Gets valid user credentials from storage.
#
#     If nothing has been stored, or if the stored credentials are invalid,
#     the OAuth2 flow is completed to obtain the new credentials.
#
#     Returns:
#         Credentials, the obtained credential.
#     """
#     home_dir = os.path.expanduser('~')
#     credential_dir = os.path.join(home_dir, '.credentials')
#     if not os.path.exists(credential_dir):
#         os.makedirs(credential_dir)
#     credential_path = os.path.join(
#         credential_dir,
#         'sheets.googleapis.com-python-quickstart.json')
#
#     store = Storage(credential_path)
#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#         flow.user_agent = APPLICATION_NAME
#         credentials = tools.run_flow(flow, store)
#         print('Storing credentials to ' + credential_path)
#     return credentials


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

    def add_dish(self, list_dish):
        self.dishes.append(Dish(list_dish))


# api_auth = OAuth2DecoratorFromClientSecrets(
#     os.path.join(os.path.dirname(__file__), CLIENT_SECRET_FILE), SCOPES)


# @api_auth.oauth_required
# def get_menu_info():
#     """Shows basic usage of the Sheets API.
#
#     Creates a Sheets API service object and prints the names and majors of
#     students in a sample spreadsheet:
#     https://docs.google.com/spreadsheets/d/1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno/edit
#     """
#     # credentials = get_credentials()
#     # credentials = DEFAULT_CREDENTIALS
#     # http = credentials.authorize(httplib2.Http())
#     # discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
#     #                 'version=v4')
#     # service = discovery.build('sheets', 'v4', http=http,
#     #                           discoveryServiceUrl=discoveryUrl)
#     # service = discovery.build('sheets', 'v4', credentials=credentials)
#     service = discovery.build('sheets', 'v4')
#
#     # Get the authorized Http object created by the api_auth.
#     # http = api_auth.http()
#
#     spreadsheet_id = '1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno'
#     range_name = 'menu!A2:G'
#
#     # Call the service using the authorized Http object.
#     request = service.spreadsheets().values().get(
#         spreadsheetId=spreadsheet_id, range=range_name)
#     response = request.execute(http=http)
#     values = response.get('values', [])
#
#     categories = {}
#
#     if not values:
#         logging.exception('Google spreadsheet read fails.')
#         # TODO: Read cached page
#     else:
#         for row in values:
#             if row[0] in categories:
#                 categories[row[0]].add_dish(row)
#             else:
#                 categories[row[0]] = MenuCategory(row)
#         # TODO: Cache page
#
#     return categories


def get_menu_info(http=None, credentials=None):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno/edit
    """

    # flow = OAuth2WebServerFlow()
    # user = users.get_current_user()
    # memcache.set(user.user_id(), pickle.dumps(flow))
    #
    # flow = pickle.loads(memcache.get(user.user_id()))

    http = oauth2.http()
    # credentials = oauth2.credentials
    # menu = get_menu_info(http=http, credentials=credentials)
    # menu = get_menu_info(http=http)

    service = discovery.build('sheets', 'v4')

    # Get the authorized Http object created by the api_auth.
    # http = api_auth.http()

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
