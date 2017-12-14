from __future__ import print_function

import logging

from gae_api_utils import get_sheets_info


# Spreadsheet information
SHEET_ID = '1Y9U6GlDPvZYDHeltPQV-M9GhFENL7f2TvBncMByKIno'
SHEET_RANGE = 'menu!A2:G'


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


def get_menu_info():

    # Get menu sheet info.
    sheet_info = get_sheets_info(SHEET_ID, SHEET_RANGE)

    categories = {}

    if not sheet_info:
        logging.exception('No menu data.')
        print('No menu data.')
    else:
        # Initialize menu variables
        for row in sheet_info:
            if row[0] in categories:
                categories[row[0]].add_dish(row)
            else:
                categories[row[0]] = MenuCategory(row)
        for category in categories:
            categories[category].divide_group()

        logging.info('Menu information loaded.')
        print('Menu information loaded.')

    return categories
