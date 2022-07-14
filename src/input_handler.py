import keyboard
import inspect

import utils


class InputHandler:
    def __init__(self, driver, config):
        self.__driver = driver
        self.__config = config
        self.__is_toggle_autoplay_pressed = False
        self.__is_next_move_pressed = False
        self.__is_display_hint_pressed = False
        self.__is_quit_pressed = False

    def poll_toggle_autoplay_input(self):
        func_name = inspect.currentframe().f_code.co_name

        if keyboard.is_pressed(self.__config['Keybinds']['toggle_autoplay']):
            if not self.__is_toggle_autoplay_pressed:
                value = not self.__config.getboolean('Misc', 'autoplay')
                self.__config['Misc']['autoplay'] = str(value)

                self.__is_toggle_autoplay_pressed = True

                utils.log(self.__config.getboolean('Misc', 'debug'),
                          f'Autoplay: {value}', func_name)
        else:
            self.__is_toggle_autoplay_pressed = False

    def poll_next_move_input(self):
        if keyboard.is_pressed(self.__config['Keybinds']['next_move']):
            if not self.__is_next_move_pressed:
                self.__is_next_move_pressed = True
        else:
            self.__is_next_move_pressed = False

        return self.__is_next_move_pressed

    def poll_display_hint_input(self):
        if keyboard.is_pressed(self.__config['Keybinds']['display_hint']):
            if not self.__is_display_hint_pressed:
                self.__is_display_hint_pressed = True
        else:
            self.__is_display_hint_pressed = False

        return self.__is_display_hint_pressed

    def poll_quit_input(self):
        if keyboard.is_pressed(self.__config['Keybinds']['quit']):
            if not self.__is_quit_pressed:
                self.__is_quit_pressed = True
        else:
            self.__is_quit_pressed = False

        return self.__is_quit_pressed
