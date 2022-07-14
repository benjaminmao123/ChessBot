import platform
import os


def clear_console():
    if platform.uname()[0] == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def log(is_debug, message, func_name=''):
    if is_debug:
        print(f'[{func_name}] {message}')


def click_on_element(ac, element):
    ac.move_to_element(element)
    ac.click()


def click_on_square(ac, board, square):
    square_width = board.get_square_size()['width']
    square_height = board.get_square_size()['height']
    board_element = board.get_board_element()

    board_location_x = -board_element.location['x'] - square_width
    board_location_y = -square_height * 4

    distance_x = square['x'] - board_element.location['x']
    distance_y = square['y'] - board_element.location['y']

    x = board_location_x + distance_x
    y = board_location_y + distance_y

    ac.move_to_element_with_offset(board_element, x, y)
    ac.click()


def right_click_on_square(ac, board, square):
    square_width = board.get_square_size()['width']
    square_height = board.get_square_size()['height']
    board_element = board.get_board_element()

    board_location_x = -board_element.location['x'] - square_width
    board_location_y = -square_height * 4

    distance_x = square['x'] - board_element.location['x']
    distance_y = square['y'] - board_element.location['y']

    x = board_location_x + distance_x
    y = board_location_y + distance_y

    ac.move_to_element_with_offset(board_element, x, y)
    ac.context_click()
