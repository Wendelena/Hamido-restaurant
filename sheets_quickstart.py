from __future__ import print_function
import httplib2
import os

import logging

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


class Dish:
    def __init__(self, list_dish):
        self.dish_name = list_dish[3]
        self.prices = [list_dish[i] for i in range(4, len(list_dish))]


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
        for i in range(int(round(float(len(self.dishes)) / 2))):
            self.dishes_col1.append(self.dishes[i])
        for i in range(int(round(float(len(self.dishes)) / 2)),
                       len(self.dishes)):
            self.dishes_col2.append(self.dishes[i])

    def __str__(self):
        result = "content_id: {0} category_id: {1} category_name: {2}\n" \
                 "section_id: {3} carousel_id: {4} carousel_title: {5}\n" \
                 "img_url: {6}\n".format(
                     self.content_id, self.category_id, self.category_name,
                     self.section_id, self.carousel_id, self.category_name,
                     self.img_url)
        result += "dishes:\n"
        if len(self.dishes_col1) == 0 or len(self.dishes_col2) == 0:
            for dish in self.dishes:
                result += "{0}: ".format(dish.dish_name)
                for price in dish.prices:
                    result += "{0} ".format(price)
                result += "\n"
        else:
            for dish in self.dishes_col1:
                result += "{0}: ".format(dish.dish_name)
                for price in dish.prices:
                    result += "{0} ".format(price)
                result += "\n"
            result += "-----\n"
            for dish in self.dishes_col2:
                result += "{0}: ".format(dish.dish_name)
                for price in dish.prices:
                    result += "{0} ".format(price)
                result += "\n"
        result += "----------\n"
        return result


def get_credentials():

    # http = oauth2.http()
    # return http

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials


def get_menu_info(http=None, credentials=None):

    # Credentials
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')

    # Http
    # service = discovery.build('sheets', 'v4')
    # Credentials
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheet_id = '1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno'
    range_name = 'menu!A2:G'

    # Call the service using the authorized Http object.
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name)

    # Http
    # response = request.execute(http=http)
    # Credentials
    response = request.execute()

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
            categories[category].divide_group()
    # TODO: Cache page

    return categories


def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno/edit
    """
    credentials = get_credentials()
    menu = get_menu_info(credentials=credentials)

    if not menu:
        print('No data found.')
    else:
        for category in menu:
            print(menu[category])


if __name__ == '__main__':
    main()
