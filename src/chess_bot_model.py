from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import inspect

from parser import Parser
import utils
import strings


class ChessBotModel:
    def __init__(self, driver, config, board, engine, bot):
        self.__driver = driver
        self.__config = config
        self.__board = board
        self.__engine = engine
        self.__chess_bot = bot
        self.__next_move = None

    def display_next_move(self):
        func_name = inspect.currentframe().f_code.co_name

        if not self.__next_move:
            self.__next_move = self.__get_next_move()

            if not self.__next_move:
                return

        h_elements = self.__driver.find_elements(By.CSS_SELECTOR, strings.highlighted_elements)

        src_square_num = Parser.letters_to_numbers[self.__next_move['squares'][0][-2:-1]] + \
                         self.__next_move['squares'][0][-1]

        if h_elements:
            for e in h_elements:
                if src_square_num in e.get_attribute('class'):
                    if strings.display_hint_highlight_color == e.value_of_css_property('background-color'):
                        return

        x, y = self.__compute_offsets()

        utils.log(self.__config.getboolean('Misc', 'debug'), f'Move: ({x}, {y})', func_name)

        ac = ActionChains(self.__driver)
        utils.context_click_on_element(self.__next_move['element'], ac)
        utils.context_click_on_element_offset(self.__next_move['element'], ac, x, y)
        ac.perform()

    def play_next_move(self):
        func_name = inspect.currentframe().f_code.co_name

        if not self.__next_move:
            self.__next_move = self.__get_next_move()

            if not self.__next_move:
                return

        x, y = self.__compute_offsets()

        utils.log(self.__config.getboolean('Misc', 'debug'), f'Move: ({x}, {y})', func_name)

        ac = ActionChains(self.__driver)
        utils.click_on_element(self.__next_move['element'], ac)
        utils.click_on_element_offset(self.__next_move['element'], ac, x, y)
        ac.perform()

        if self.__next_move['promotion'][0]:
            promo_pieces = self.__driver.find_elements(By.CSS_SELECTOR, strings.promotion_pieces)

            if promo_pieces:
                for piece in promo_pieces:
                    piece_name = piece.get_attribute('class')[-2]

                    if piece_name == self.__next_move['promotion'][1]:
                        utils.click_on_element(piece, ac)
                        ac.perform()
                        break

        self.__board.update_board()

    def reset(self):
        self.__next_move = None

    def __compute_offsets(self):
        if not self.__next_move:
            return None, None

        src_x, src_y = self.__board.get_board_element(self.__next_move['squares'][0])['x'], \
                       self.__board.get_board_element(self.__next_move['squares'][0])['y']
        dest_x, dest_y = self.__board.get_board_element(self.__next_move['squares'][1])['x'], \
                         self.__board.get_board_element(self.__next_move['squares'][1])['y']

        x = dest_x - src_x
        y = dest_y - src_y

        return x, y

    def __get_next_move(self):
        self.__next_move = None

        if self.__board.is_player_turn():
            fen = self.__board.generate_fen()
            self.__engine.update_fen(fen)

            move = self.__engine.get_best_move()

            res = Parser.parse_move_from_engine(move, self.__board)

            src_square, dest_square = res['squares'][0][0], res['squares'][0][1]
            src_element = self.__board.get_board_element(res['squares'][0][0])['element']

            self.__next_move = {'squares': (src_square, dest_square), 'element': src_element,
                                'promotion': res['promotion']}

        return self.__next_move
