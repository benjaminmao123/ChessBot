import keyboard
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import element_strings
from board import Board
from engine import Engine
import utils


class ChessBot:
    def __init__(self, config):
        self.__is_debug = config.getboolean('Misc', 'debug')
        self.__init_driver()
        self.__config = config

        self.__board = Board(self.__driver, self.__is_debug)
        self.__engine = Engine(config)
        self.__is_player_turn = True
        self.__is_playing = False
        self.__autoplay = config.getboolean('Misc', 'autoplay')

    def __init_driver(self):
        self.__options = Options()
        self.__options.binary_location = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
        self.__options.add_experimental_option("excludeSwitches", ['enable-automation'])

        self.__driver = webdriver.Chrome(executable_path='assets/chromedriver.exe', options=self.__options)
        self.__driver.maximize_window()
        self.__driver.get('https://www.chess.com/play/online')

    def run(self):
        on_play = True
        key_pressed = False

        while True:
            try:
                self.__update_state()

                if self.__is_playing:
                    if on_play:
                        self.__board.init_board()
                        self.__is_player_turn = not self.__board.is_flipped()
                        on_play = False

                    if self.__board.update_board():
                        self.__is_player_turn = True

                        if self.__is_debug:
                            utils.log('__run', f'Turn = {self.__is_player_turn}')

                    if self.__is_player_turn:
                        if self.__autoplay:
                            self.__evaluate_and_move()
                            self.__is_player_turn = False
                        else:
                            if not key_pressed and keyboard.is_pressed('enter'):
                                self.__evaluate_and_move()
                                self.__is_player_turn = False
                                key_pressed = True
                            else:
                                key_pressed = False

                        if self.__is_debug:
                            utils.log('__run', f'Turn = {self.__is_player_turn}')
                else:
                    on_play = True
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

    def run_test(self):
        on_play = True

        while True:
            try:
                if not self.__is_playing:
                    if input() == 'start':
                        self.__is_playing = True

                if self.__is_playing:
                    if on_play:
                        self.__board.init_board()
                        on_play = False

                    fen_move = input("Move: ")
                    
                    if self.__evaluate_and_move(fen_move):
                        self.__is_player_turn = False
                else:
                    on_play = True
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

    def __update_state(self):
        if not self.__is_playing:
            if self.__driver.find_elements(By.CSS_SELECTOR, element_strings.resign_button) or \
                    self.__driver.find_elements(By.CSS_SELECTOR, element_strings.resign_button_cpu):
                self.__is_playing = True

                if self.__is_debug:
                    utils.log('__update_state', f'State: {self.__is_playing}')
        else:
            if self.__driver.find_elements(By.CSS_SELECTOR, element_strings.game_over):
                self.__is_playing = False

                if self.__is_debug:
                    utils.log('__update_state', f'State: {self.__is_playing}')

    def __evaluate_and_move(self, player_fen=None):
        if not player_fen:
            fen = self.__board.generate_fen()
            self.__engine.update_engine(fen)

            move = self.__engine.get_best_move(self.__config.getint('Engine', 'best_move_time_limit'))

            if self.__is_debug:
                utils.log('__evaluate_and_move', f'Player Move: {move}')

            return self.__board.move(move)

        self.__board.move(player_fen)

    def __determine_turn_restart(self):
        white_active_timer = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.white_player_turn_timer)
        black_active_timer = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.black_player_turn_timer)
        white_inactive_timer = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.white_player_opponent_turn)
        black_inactive_timer = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.black_player_opponent_turn)

        if white_active_timer or black_active_timer:
            self.__is_playing = True
        if black_active_timer or black_inactive_timer:
            self.__board.flip_board()
        if white_inactive_timer or black_inactive_timer:
            self.__is_playing = False

    def __restart(self):
        self.__determine_turn_restart()
        self.__board.rebuild()
