from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

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
        if not self.__next_move:
            self.__next_move = self.__get_next_move()

            if not self.__next_move:
                return

        h_elements = self.__driver.find_elements(By.CSS_SELECTOR, strings.highlighted_elements)

        src_square_name = self.__next_move['square_name'][0]

        src_square_num = Parser.letters_to_numbers[src_square_name[-2:-1]] + src_square_name[-1]

        if h_elements:
            for e in h_elements:
                if src_square_num in e.get_attribute('class'):
                    if strings.display_hint_highlight_color == e.value_of_css_property('background-color'):
                        return

        ac = ActionChains(self.__driver)
        utils.right_click_on_square(ac, self.__board.get_board_element(), self.__next_move['square'][0])
        utils.right_click_on_square(ac, self.__board.get_board_element(), self.__next_move['square'][1])
        ac.perform()

    def play_next_move(self):
        if not self.__next_move:
            self.__next_move = self.__get_next_move()

            if not self.__next_move:
                return

        ac = ActionChains(self.__driver)
        utils.click_on_square(ac, self.__board.get_board_element(), self.__next_move['square'][0])
        utils.click_on_square(ac, self.__board.get_board_element(), self.__next_move['square'][1])
        ac.perform()

        if self.__next_move['promotion'][0]:
            promo_pieces = self.__driver.find_elements(By.CSS_SELECTOR, strings.promotion_pieces)

            if promo_pieces:
                for piece in promo_pieces:
                    piece_name = piece.get_attribute('class')[-2]

                    if piece_name == self.__next_move['promotion'][1]:
                        utils.click_on_element(ac, piece)
                        ac.perform()
                        break

        self.__board.update_board()

    def reset(self):
        self.__next_move = None

    def __get_next_move(self):
        self.__next_move = None

        if self.__board.is_player_turn():
            fen = self.__board.generate_fen()
            self.__engine.update_fen(fen)

            move = self.__engine.get_best_move()

            res = Parser.parse_move_from_engine(move, self.__board)

            src_square_name, dest_square_name = res['squares'][0][0], res['squares'][0][1]
            src_square, dest_square = self.__board.get_board_map_element(src_square_name), \
                                      self.__board.get_board_map_element(dest_square_name)

            self.__next_move = {'square_name': (src_square_name, dest_square_name),
                                'square': (src_square, dest_square),
                                'promotion': res['promotion']}

        return self.__next_move
