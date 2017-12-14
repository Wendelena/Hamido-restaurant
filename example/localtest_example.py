# Test menu functions locally

from hamido_menu import get_menu_info


if __name__ == '__main__':
    categories = get_menu_info(cached=False)
    for category in categories:
        print(categories[category])
