from __future__ import print_function

import logging
import pickle

from oauth2client.client import HttpAccessTokenRefreshError

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


def get_info_from_cache():
    logging.info('Read from cache...')
    if LOCAL:
        print('Read from cache...')
        # Read cached info
        try:
            with open(MENU_CACHE, 'r') as cache:
                values = pickle.loads(cache.read())
        except:
            values = None
            logging.warning('File reading error. Unable to get info.')
    else:
        # Read cached info from memcache
        try:
            values = pickle.loads(memcache.get(MENU_KEY))
        except TypeError:
            values = None
            logging.warning('Type error. Unable to get info.')
        except:
            values = None
            logging.exception('New error. Unable to get info.')

    return values


def set_info_in_cache(values):
    logging.info('Set values in cache...')
    if LOCAL:
        print('Set values in cache...')
        # Cache page
        with open(MENU_CACHE, 'w') as cache:
            cache.write(pickle.dumps(values))
    else:
        # Cache page into memcache
        memcache.set(MENU_KEY, pickle.dumps(values))

    # Set EVER_CACHED
    global EVER_CACHED
    EVER_CACHED = True
    logging.info('Cache set.')
    logging.info('EVER_CACHED = ' + str(EVER_CACHED))
    if LOCAL:
        print('Cache set.')
        print('EVER_CACHED = ' + str(EVER_CACHED))


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

    elif OAUTH2:
        try:
            http = OAUTH2.http()
        except ValueError:
            logging.exception('No credentials available.')
            http = None

    else:
        logging.exception('Flask app OAuth not setup.')
        http = None

    return http


def get_sheets_info(sheet_id, sheet_range, cached=True):
    global EVER_CACHED
    if EVER_CACHED and cached:
        # Getting from cache
        logging.warning('Acquiring cached info...')
        if LOCAL:
            print('Acquiring cached info...')

        # Read cache
        values = get_info_from_cache()

        if not values:
            logging.exception('Cache read fails.')
            if LOCAL:
                print('Cache read fails.')
            return None
        else:
            logging.info('Cached info acquired.')
            if LOCAL:
                print('Cached info acquired.')
            return values

    elif cached:
        # Invalid input: read cache before first caching
        logging.warning('Invalid input: read cache before first caching.')
        if LOCAL:
            print('Invalid input: read cache before first caching.')
        return None

    # Requesting API (cached = False)
    logging.warning('Acquiring info from Google Sheets API...')
    if LOCAL:
        print('Acquiring info from Google Sheets API...')

    # Setting up service
    if LOCAL:
        # OAuth2 in local Python python environment
        http = get_auth_http()
        if http:
            service = discovery.build('sheets', 'v4', http=http,
                                      discoveryServiceUrl=API_URL)
        else:
            logging.exception('API request fails.')
            print('API request fails.')
            return None

    elif OAUTH2:
        # OAuth2 through GAE
        http = get_auth_http()
        if http:
            service = discovery.build('sheets', 'v4', http=http)
        else:
            logging.exception('API request fails.')
            return None
    else:
        # OAuth2 not setup on GAE
        logging.exception('Flask app OAuth not setup. API request fails.')
        return None

    # Executing request and getting results
    try:
        # Call the service using the authorized Http object.
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        values = result.get('values', [])
    except HttpAccessTokenRefreshError:
        logging.exception('Invalid grant. Bad request. API request fails.')
        if LOCAL:
            print('Invalid grant. Bad request. API request fails.')
        return None

    if not values:
        # Info got from request invalid, fall back to cache
        logging.warning('Google spreadsheet read results invalid.')
        if LOCAL:
            print('Google spreadsheet read results invalid.')

        values = get_info_from_cache()

        if not values:
            logging.exception('Cache read fails.')
            if LOCAL:
                print('Cache read fails.')
            return None

    else:
        # Values acquired
        logging.info('Values acquired from Google Sheets API.')
        if LOCAL:
            print('Values acquired from Google Sheets API.')

        # Cache page
        set_info_in_cache(values)

    return values
