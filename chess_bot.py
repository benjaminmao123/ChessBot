import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import element_strings
from board import Board
from engine import Engine
import utils
import keyboard


class ChessBot:
    def __init__(self, debug=False):
        self.__is_debug = debug
        self.__init_driver()

        self.__board = Board(self.__driver, debug)
        self.__engine = Engine()
        self.__is_player_turn = True
        self.__is_playing = False

    def __init_driver(self):
        self.__options = Options()
        self.__options.binary_location = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
        self.__options.add_experimental_option("detach", True)
        self.__options.add_experimental_option("excludeSwitches", ['enable-automation'])

        self.__driver = webdriver.Chrome(executable_path='assets/chromedriver.exe', options=self.__options)
        self.__driver.maximize_window()
        self.__driver.get('https://www.chess.com/play/online')

    def run(self):
        on_play = True
        is_key_pressed = False
        is_running = True

        while is_running:
            try:
                self.__update_state()

                if self.__is_playing:
                    if on_play:
                        self.__board.init_board()
                        self.__is_player_turn = not self.__board.is_flipped()
                        on_play = False

                    if not is_key_pressed and keyboard.is_pressed('f5'):
                        is_running = False
                        is_key_pressed = True
                    else:
                        is_key_pressed = False

                    if self.__board.update_board():
                        self.__is_player_turn = True

                        if self.__is_debug:
                            utils.log('__run', f'Turn = {self.__is_player_turn}')

                    if self.__is_player_turn:
                        self.__evaluate_and_move()
                        self.__is_player_turn = False

                        if self.__is_debug:
                            utils.log('__run', f'Turn = {self.__is_player_turn}')
                else:
                    on_play = True
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

    def __update_state(self):
        if self.__driver.find_elements(By.CSS_SELECTOR, element_strings.resign_button):
            self.__is_playing = True
        if self.__driver.find_elements(By.CSS_SELECTOR, element_strings.resign_button_cpu):
            self.__is_playing = True
        if self.__driver.find_elements(By.CSS_SELECTOR, element_strings.game_over):
            self.__is_playing = False

    def __evaluate_and_move(self):
        fen = self.__board.generate_fen()
        self.__engine.update_engine(fen)

        move = self.__engine.get_best_move()

        if self.__is_debug:
            utils.log('__evaluate_and_move', f'Player Move: {move}')

        self.__board.move(move)
