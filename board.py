import chess
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import utils
import element_strings


class Board:
    def __init__(self, driver, debug=False):
        self.__is_debug = debug
        self.__chess_lib_board = chess.Board()
        self.__driver = driver
        self.__board = {}
        self.__is_flipped = False

        self.__letters_to_numbers = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
        self.__numbers_to_letters = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
        self.__fen_to_name = {'R': 'wr', 'N': 'wn', 'B': 'wb', 'Q': 'wq', 'K': 'wk', 'r': 'br', 'n': 'bn', 'b': 'bb',
                              'q': 'bq',
                              'k': 'bk'}
        self.__name_to_fen = {'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K', 'br': 'r', 'bn': 'n', 'bb': 'b',
                              'bq': 'q',
                              'bk': 'k'}

    def init_board(self):
        self.__reset_board()

        for k, v in self.__letters_to_numbers.items():
            for j in range(1, 9):
                self.__board[k + str(j)] = None

        squares = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.squares)

        indices_white = [i for i, x in enumerate(squares) if 'wr' in x.get_attribute('class')]
        indices_black = [i for i, x in enumerate(squares) if 'br' in x.get_attribute('class')]

        if not self.__is_flipped:
            if squares[indices_white[0]].location['y'] < squares[indices_black[0]].location['y']:
                self.__is_flipped = True
            else:
                self.__is_flipped = False

        if self.__is_flipped:
            if squares[indices_black[0]].location['x'] < squares[indices_black[1]].location['x']:
                bottom_left = squares[indices_black[0]]
            else:
                bottom_left = squares[indices_black[1]]
        else:
            if squares[indices_white[0]].location['x'] < squares[indices_white[1]].location['x']:
                bottom_left = squares[indices_white[0]]
            else:
                bottom_left = squares[indices_white[1]]

        col = 0

        if not self.__is_flipped:
            for k in self.__letters_to_numbers.keys():
                for row in range(1, 9):
                    self.__board[k + str(row)] = {'x': bottom_left.location['x'] + bottom_left.size['width'] * col,
                                                  'y': bottom_left.location['y'] - bottom_left.size['height'] * (row - 1),
                                                  'element': None, 'piece': None}

                col += 1
        else:
            for k in reversed(list(self.__letters_to_numbers.keys())):
                row_actual = 0

                for row in range(8, 0, -1):
                    self.__board[k + str(row)] = \
                        {'x': bottom_left.location['x'] + bottom_left.size['width'] * col,
                         'y': bottom_left.location['y'] - bottom_left.size['height'] * row_actual,
                         'element': None, 'piece': None}

                    row_actual += 1

                col += 1

        for square in squares:
            class_name = square.get_attribute('class')

            try:
                letter = self.__numbers_to_letters[int(class_name[-2:-1])]
                number = class_name[-1]
                piece_name = class_name[6:8]
            except ValueError:
                letter = self.__numbers_to_letters[int(class_name[-5:-4])]
                number = class_name[-4]
                piece_name = class_name[-2:]

            self.__board[letter + str(number)]['element'] = square
            self.__board[letter + str(number)]['piece'] = piece_name

    def update_board(self):
        highlighted_elements = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.highlighted_elements)

        if not highlighted_elements:
            return False

        if not self.__is_flipped:
            last_move = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.black_node)
        else:
            last_move = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.white_node)

        if last_move:
            last_move = last_move[0].text
        else:
            return False

        try:
            self.push_move(last_move)
        except ValueError:
            return False

        if self.__is_debug:
            utils.log('update_board', f'Opponent Move: {last_move}')

        res_squares = self.__parse_opponent_move(last_move, highlighted_elements)

        for square in res_squares:
            self.__overwrite_element(square[0], square[1])

        return True

    def __parse_opponent_move(self, arg, h_elements, ):
        arg = arg.replace('x', '')
        arg = arg.replace('+', '')

        if arg == 'O-O':
            if self.__is_flipped:
                return [('e1', 'g1'), ('h1', 'f1')]
            else:
                return [('e8', 'g8'), ('h8', 'f8')]
        elif arg == 'O-O-O':
            if self.__is_flipped:
                return [('e1', 'c1'), ('a1', 'd1')]
            else:
                return [('e8', 'c8'), ('a8', 'd8')]

        dest_square_num = str(self.__letters_to_numbers[arg[-2:-1]]) + arg[-1]
        dest_square = arg[-2:]
        src_square = None
        name = None

        for e in h_elements:
            name = e.get_attribute('class')

            if dest_square_num not in name:
                break

        for i, c in enumerate(name):
            if c.isdigit():
                square_num = name[i:]
                src_square = self.__numbers_to_letters[int(square_num[0])] + square_num[1]
                break

        return [(src_square, dest_square)]

    def generate_fen(self):
        return self.__chess_lib_board.fen()

    def push_move(self, move):
        if self.__is_debug:
            utils.log('push_move', f'Push Move: {move}')

        self.__chess_lib_board.push_san(move)

        if self.__is_debug:
            utils.log('push_move', f'\n{self.__chess_lib_board}')

    def __overwrite_element(self, src, dest):
        src_element = self.__board[src]['element']
        src_piece = self.__board[src]['piece']

        self.__board[src]['element'] = None
        self.__board[src]['piece'] = None
        self.__board[dest]['element'] = src_element
        self.__board[dest]['piece'] = src_piece

        return src_element, src_piece

    def __parse_player_move(self, san):
        san = san.replace('x', '')
        san = san.replace('+', '')

        is_castle_king = False
        is_castle_queen = False
        is_promotion = False
        promotion_piece_name = None

        if san == 'O-O' or san == 'e8g8' or san == 'e1g1':
            if self.__is_flipped:
                src_square, dest_square = 'e8', 'g8'
            else:
                src_square, dest_square = 'e1', 'g1'

            is_castle_king = True
        elif san == 'O-O-O' or san == 'e8c8' or san == 'e1c1':
            if self.__is_flipped:
                src_square, dest_square = 'e8', 'c8'
            else:
                src_square, dest_square = 'e1', 'c1'

            is_castle_queen = True
        elif len(san) == 3:
            piece_name = self.__fen_to_name[san[0]]
            src_square = None
            dest_square = san[-2:]
            potential_squares = []

            for k, v in self.__board.items():
                if v['piece'] == piece_name:
                    potential_squares.append(k)

            for square in potential_squares:
                move = chess.Move.from_uci(square + dest_square)

                if self.__chess_lib_board.is_legal(move):
                    src_square = square
                    break
        elif len(san) == 4:
            src_square = san[0:2]
            dest_square = san[2:]
        else:
            if self.__is_flipped:
                promotion_piece_name = self.__fen_to_name[san[-1]]
            else:
                promotion_piece_name = self.__fen_to_name[san[-1].upper()]

            is_promotion = True

            src_square = san[0:2]
            dest_square = san[2:-1]

        return src_square, dest_square, (is_castle_king, is_castle_queen), (is_promotion, promotion_piece_name)

    def move(self, fen):
        src_square, dest_square, castle, promotion = self.__parse_player_move(fen)

        try:
            self.push_move(fen)
        except ValueError:
            return False

        if castle[0]:
            if self.__is_flipped:
                self.__overwrite_element('h8', 'f8')
            else:
                self.__overwrite_element('h1', 'f1')
        elif castle[1]:
            if self.__is_flipped:
                self.__overwrite_element('a8', 'd8')
            else:
                self.__overwrite_element('a1', 'd1')

        if self.__is_debug:
            utils.log('move', f'Player Click: (Src: {src_square}, Dest: {dest_square})')

        self.__move_click(src_square, dest_square, promotion)

        return True

    def __move_click(self, src, dest, promotion=(False, None)):
        src_element, src_piece = self.__overwrite_element(src, dest)

        ac = ActionChains(self.__driver)
        ac.move_to_element(src_element)
        ac.click()

        x = self.__board[dest]['x'] - self.__board[src]['x']
        y = self.__board[dest]['y'] - self.__board[src]['y']

        ac.move_to_element_with_offset(src_element, x, y)
        ac.click()
        ac.perform()

        if promotion[0]:
            promo_pieces = self.__driver.find_elements(By.CSS_SELECTOR, element_strings.promotion_pieces)

            if promo_pieces:
                for piece in promo_pieces:
                    piece_name = piece.get_attribute('class')[-2:]

                    if piece_name == promotion[1]:
                        ac.move_to_element(piece)
                        ac.click()
                        ac.perform()
                        break

            promo_square = str(self.__letters_to_numbers[dest[0]]) + dest[1]
            promo_element = self.__driver.find_elements(By.CSS_SELECTOR, f'.square-{promo_square}')
            self.__board[dest]['element'] = promo_element[0]
            self.__board[dest]['piece'] = promotion[1]

    def __reset_board(self):
        self.__chess_lib_board = chess.Board()
        self.__board = {}
        self.__is_flipped = False

    def is_flipped(self):
        return self.__is_flipped

    def flip_board(self):
        self.__is_flipped = True
        self.rebuild()

    def rebuild(self):
        pass