import platform
import os


def clear_console():
    if platform.uname()[0] == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def log(func_name, message):
    print(f'{func_name}: {message}')
