import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import inspect

import strings
from board import Board
from engine import Engine
import utils
from input_handler import InputHandler
from chess_bot_model import ChessBotModel


class ChessBot:
    def __init__(self, config):
        self.__config = config

        self.__init_driver()

        self.__board = Board(self.__driver, self.__config, self)
        self.__engine = Engine(self.__config)
        self.__input_handler = InputHandler(self.__driver, self.__config)
        self.__chess_bot_model = ChessBotModel(self.__driver, self.__config, self.__board, self.__engine, self)
        self.__is_playing = False

    def __init_driver(self):
        self.__options = Options()
        self.__options.binary_location = self.__config.get('Path', 'chrome_binary')
        self.__options.add_experimental_option("excludeSwitches", ['enable-automation'])

        self.__driver = webdriver.Chrome(executable_path=self.__config.get('Path', 'web_driver'),
                                         options=self.__options)
        self.__driver.maximize_window()
        self.__driver.get(self.__config.get('Path', 'url'))

    def run(self):
        board_initialized = False
        quit_app = False

        while not quit_app:
            try:
                board_initialized, quit_app = self.__update(board_initialized)

            except selenium.common.exceptions.StaleElementReferenceException:
                pass

        self.__driver.quit()

    def __update(self, board_initialized):
        self.update_state()

        self.__input_handler.poll_toggle_autoplay_input()
        quit_app = self.__input_handler.poll_quit_input()

        if self.__is_playing:
            if not board_initialized:
                self.__board.init()
                self.__chess_bot_model.reset()
                board_initialized = True

            self.__chess_bot_model.reset()
            self.__board.update_board()

            if self.__input_handler.poll_display_hint_input():
                self.__chess_bot_model.display_next_move()
            if self.__config.getboolean('Misc', 'autoplay'):
                self.__chess_bot_model.play_next_move()
            elif self.__input_handler.poll_next_move_input():
                self.__chess_bot_model.play_next_move()
        else:
            board_initialized = False
            self.__board.reset_board()

        return board_initialized, quit_app

    def update_state(self):
        func_name = inspect.currentframe().f_code.co_name

        if not self.__is_playing:
            if self.__driver.find_elements(By.CSS_SELECTOR, strings.resign_button):
                self.__is_playing = True
            if 'analysis' in self.__driver.current_url:
                if not self.__board.board_in_checkmate():
                    self.__is_playing = True

            if self.__is_playing:
                utils.log(self.__config.getboolean('Misc', 'debug'),
                          f'Is Playing: {self.__is_playing}', func_name)
        else:
            if self.__driver.find_elements(By.CSS_SELECTOR, strings.game_over) or \
                    self.__driver.find_elements(By.XPATH, strings.game_over_text) or \
                    ('analysis' not in self.__driver.current_url and
                     'game' not in self.__driver.current_url and
                     'computer' not in self.__driver.current_url) or \
                    self.__driver.find_elements(By.CSS_SELECTOR, strings.game_result):
                self.__is_playing = False
            if 'analysis' in self.__driver.current_url:
                if self.__board.board_in_checkmate():
                    self.__is_playing = False
            if not self.__is_playing:
                utils.log(self.__config.getboolean('Misc', 'debug'),
                          f'Is Playing: {self.__is_playing}', func_name)
