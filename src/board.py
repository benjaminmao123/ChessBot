import chess
from selenium.webdriver.common.by import By
import inspect

import utils
import strings
from parser import Parser
from collections import deque


class Board:
    def __init__(self, driver, config, bot):
        self.__driver = driver
        self.__config = config
        self.__chess_bot = bot

        self.__overwrite_element_queue = deque()
        self.__board = chess.Board()
        self.__board_mapping = {}
        self.__prev_move = None
        self.__turn = True
        self.__is_board_in_checkmate = False
        self.__prev_move_list = None
        self.__board_element = None
        self.__square_size = {'width': 0, 'height': 0}

        self.__init_default_piece_location()

    def init(self):
        self.reset_board()

        for row_num in range(1, 9):
            for col_name in Parser.letters_to_numbers.keys():
                self.__board_mapping[col_name + str(row_num)] = None

        if self.is_flipped():
            self.__board_element = self.__driver.find_elements(By.CSS_SELECTOR, strings.board_flipped)[0]

            row_start, row_end, row_increment = 1, 9, 1
            col_start, col_end, col_increment = 8, 0, -1
        else:
            self.__board_element = self.__driver.find_elements(By.CSS_SELECTOR, strings.board)[0]

            row_start, row_end, row_increment = 8, 0, -1
            col_start, col_end, col_increment = 1, 9, 1

        self.__square_size['width'] = self.__board_element.size['width'] / 8
        self.__square_size['height'] = self.__board_element.size['height'] / 8

        square_width, square_height = self.__board_element.size['width'] / 8, self.__board_element.size['height'] / 8

        for row_num, row_offset in zip(range(row_start, row_end, row_increment), range(0, 8)):
            for col, col_offset in zip(range(col_start, col_end, col_increment), range(0, 8)):
                key = Parser.numbers_to_letters[str(col)] + str(row_num)
                piece_name = self.__default_piece_location[key] if key in self.__default_piece_location else None

                self.__board_mapping[key] = {'x': self.__board_element.location['x'] + square_width * col_offset,
                                             'y': self.__board_element.location['y'] + square_height * row_offset,
                                             'piece_name': piece_name}

    def update_board(self):
        h_elements = self.__driver.find_elements(By.CSS_SELECTOR, strings.highlighted_elements)

        if not h_elements:
            return

        for e in h_elements:
            if 'element-pool' in e.get_attribute('class'):
                return

        last_move = self.__driver.find_elements(By.CSS_SELECTOR, strings.node_selected)

        if last_move == self.__prev_move:
            return

        self.__prev_move = last_move

        if last_move:
            period_idx = last_move[0].text.find('.')

            if period_idx != -1:
                last_move = last_move[0].text.replace(" ", "")
                last_move = last_move[period_idx + 1:]
            else:
                last_move = last_move[0].text
        else:
            return

        if '#' in last_move:
            self.__is_board_in_checkmate = True
            return

        try:
            self.__push_move(last_move)
        except ValueError:
            return

        last_move = Parser.parse_move_from_site(last_move, h_elements, self.get_turn())
        self.__overwrite_elements(last_move)

        self.__turn = not self.__turn

        self.__chess_bot.update_state()
        self.__chess_bot.display_evaluation()

    def generate_fen(self):
        return self.__board.fen()

    def is_flipped(self):
        board_element = self.__driver.find_elements(By.CSS_SELECTOR, strings.board_flipped)

        if board_element:
            return True

        return False

    def get_turn(self):
        return self.__turn

    def is_player_turn(self):
        func_name = inspect.currentframe().f_code.co_name

        if self.is_flipped():
            if not self.__turn:
                utils.log(self.__config.getboolean('Misc', 'debug'), f'{True}', func_name)
                return True
        else:
            if self.__turn:
                utils.log(self.__config.getboolean('Misc', 'debug'), f'{True}', func_name)
                return True

        return False

    def get_board_map_element(self, key):
        return self.__board_mapping[key]

    def get_all_pieces_with_name(self, name):
        res = []

        for k, v in self.__board_mapping.items():
            if v['piece'] == name:
                res.append(k)

        return res

    def is_legal_move(self, move):
        return self.__board.is_legal(move)

    def board_in_checkmate(self):
        return self.__is_board_in_checkmate

    def reset_board(self):
        self.__board.reset()
        self.__board_mapping = {}
        self.__turn = True
        self.__prev_move = None
        self.__overwrite_element_queue.clear()
        self.__is_board_in_checkmate = False
        self.__board_element = None
        self.__square_size['width'], self.__square_size['y'] = 0, 0

    def get_board_element(self):
        return self.__board_element

    def get_square_size(self):
        return self.__square_size

    def __push_move(self, move):
        func_name = inspect.currentframe().f_code.co_name

        self.__board.push_san(move)

        utils.log(self.__config.getboolean('Misc', 'debug'),
                  f'Push Move: {move}\nBoard: \n{self.__board}', func_name)

    def __overwrite_elements(self, move):
        func_name = inspect.currentframe().f_code.co_name

        for square in move['squares']:
            self.__overwrite_element(square[0], square[1])

        if move['promotion'][0]:
            dest_square = move['squares'][0][1]
            self.__board_mapping[dest_square]['piece_name'] = move['promotion'][1]

            utils.log(self.__config.getboolean('Misc', 'debug'),
                      f'(Destination Square: {dest_square}, '
                      f'Destination Piece: {self.__board_mapping[dest_square]["piece_name"]})\n',
                      func_name)

    def __overwrite_element(self, src, dest):
        func_name = inspect.currentframe().f_code.co_name

        src_piece = self.__board_mapping[src]['piece_name']

        utils.log(self.__config.getboolean('Misc', 'debug'),
                  f'Before:\n(Source Square: {src}, '
                  f'Source Piece: {src_piece}), '
                  f'(Destination Square: {dest}, '
                  f'Destination Piece: {self.__board_mapping[dest]["piece_name"]})',
                  func_name)

        self.__board_mapping[src]['piece_name'] = None
        self.__board_mapping[dest]['piece_name'] = src_piece

        utils.log(self.__config.getboolean('Misc', 'debug'),
                  f'After:\n(Source Square: {src}, '
                  f'Source Piece: {self.__board_mapping[src]["piece_name"]}), '
                  f'(Destination Square: {dest}, '
                  f'Destination Piece: {self.__board_mapping[dest]["piece_name"]})\n',
                  func_name)

    def __init_default_piece_location(self):
        self.__default_piece_location = {}

        for col_letter in Parser.letters_to_numbers.keys():
            key = col_letter + str(2)
            self.__default_piece_location[key] = 'wp'

            key = col_letter + str(7)
            self.__default_piece_location[key] = 'bp'

        self.__default_piece_location['a1'] = 'wr'
        self.__default_piece_location['b1'] = 'wn'
        self.__default_piece_location['c1'] = 'wb'
        self.__default_piece_location['d1'] = 'wq'
        self.__default_piece_location['e1'] = 'wk'
        self.__default_piece_location['f1'] = 'wb'
        self.__default_piece_location['g1'] = 'wn'
        self.__default_piece_location['h1'] = 'wr'

        self.__default_piece_location['a8'] = 'br'
        self.__default_piece_location['b8'] = 'bn'
        self.__default_piece_location['c8'] = 'bb'
        self.__default_piece_location['d8'] = 'bq'
        self.__default_piece_location['e8'] = 'bk'
        self.__default_piece_location['f8'] = 'bb'
        self.__default_piece_location['g8'] = 'bn'
        self.__default_piece_location['h8'] = 'br'
