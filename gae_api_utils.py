from __future__ import print_function

import logging
import pickle

import flag_local
from apiclient import discovery

# Local environment: True; GAE: False
LOCAL = flag_local.LOCAL
EVER_CACHED = False


# Flask app OAuth2
OAUTH2 = None
# OAuth information
CLIENT_SECRET_FILE = 'client_secret.json'
# API scope
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
# Application name
APPLICATION_NAME = 'Google Sheets API Python Access'
# API URL
API_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
# Menu object key
MENU_KEY = 'Menu'
# Cache file name
MENU_CACHE = 'menu.cache'


# Python environment on GAE using Flask
# (See requirements.txt for third-party module requirements)
if not LOCAL:
    try:
        from oauth2client.contrib.flask_util import UserOAuth2
        from google.appengine.api import memcache
    except ImportError:
        logging.exception('Not in GAE environment.')
        print('Not in GAE environment.')
        UserOAuth2 = None
        memcache = None


# Local python environment
if LOCAL:
    import httplib2
    import os
    from oauth2client import client
    from oauth2client import tools
    from oauth2client.file import Storage

    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        argparse = None
        flags = None


def oauth_setup(app):
    if not LOCAL:
        global OAUTH2
        OAUTH2 = UserOAuth2(app)
        return OAUTH2
    else:
        print('No need for Flask app OAuth setup in local environment.')
        return None


def get_auth_http():

    if LOCAL:
        project_root = os.path.dirname(os.path.abspath(__file__))
        credential_path = os.path.join(project_root, 'local_secret.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            logging.info('Requesting credentials...')
            print('Requesting credentials...')
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run_flow(flow, store)
            logging.info('Storing credentials to ' + credential_path)
            print('Storing credentials to ' + credential_path)
        else:
            logging.info('Using locally stored credentials.')
            print('Using locally stored credentials.')

        http = credentials.authorize(httplib2.Http())

        return http

    else:
        if OAUTH2:
            http = OAUTH2.http()
        else:
            logging.exception('Flask app OAuth not setup.')
            http = None
        return http


def get_sheets_info(sheet_id, sheet_range, cached=True):

    if EVER_CACHED and cached:
        logging.info('Read from cache...')
        if LOCAL:
            print('Read from cache...')
            # Read cached menu
            try:
                with open(MENU_CACHE, 'r') as cache:
                    values = pickle.loads(cache.read())
            except:
                values = None
        else:
            values = pickle.loads(memcache.get(MENU_KEY))

        if not values:
            logging.info('Cache read fails. Request from API...')
            print('Cache read fails. Request from API...')
        else:
            return values

    if LOCAL:
        service = discovery.build('sheets', 'v4', http=get_auth_http(),
                                  discoveryServiceUrl=API_URL)

        # Call the service using the authorized Http object.
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        values = result.get('values', [])

    else:
        if OAUTH2:
            service = discovery.build('sheets', 'v4', http=get_auth_http())
            # Call the service using the authorized Http object.
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=sheet_range).execute()
            values = result.get('values', [])
        else:
            logging.exception('Flask app OAuth not setup.')
            return None

    if not values:
        if not cached:
            logging.exception('Google spreadsheet read fails. Read cache...')
            if LOCAL:
                print('Google spreadsheet read fails. Read cache...')
                # Read cached menu
                with open(MENU_CACHE, 'r') as cache:
                    values = pickle.loads(cache.read())
            else:
                values = pickle.loads(memcache.get(MENU_KEY))

            if not values:
                logging.error('Cache read fails.')
                print('Cache read fails.')
        else:
            logging.error('Request fails.')
            print('Request fails.')
            values = None
    else:
        logging.info('Re-acquire values from Google Sheets API.')
        if LOCAL:
            print('Re-acquire values from Google Sheets API.')
            # Cache page
            with open(MENU_CACHE, 'w') as cache:
                cache.write(pickle.dumps(values))
        else:
            # Cache page
            memcache.set(MENU_KEY, pickle.dumps(values))
        global EVER_CACHED
        EVER_CACHED = True

    return values
