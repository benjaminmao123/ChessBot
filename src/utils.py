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


def click_on_element(element, ac):
    ac.move_to_element(element)
    ac.click()


def click_on_element_offset(element, ac, x=0, y=0):
    ac.move_to_element_with_offset(element, x, y)
    ac.click()


def context_click_on_element(element, ac):
    ac.context_click(element)


def context_click_on_element_offset(element, ac, x=0, y=0):
    ac.move_to_element_with_offset(element, x, y)
    ac.context_click()
