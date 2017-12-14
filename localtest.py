from hamido_menu import get_menu_info


if __name__ == '__main__':
    menu = get_menu_info()

    if not menu:
        print('No data found.')
    else:
        for category in menu:
            print(menu[category])
