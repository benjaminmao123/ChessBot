import chess
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import utils


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

        squares = self.__driver.find_elements(By.CSS_SELECTOR, '.piece')

        indices_white = [i for i, x in enumerate(squares) if 'wr' in x.get_attribute('class')]
        indices_black = [i for i, x in enumerate(squares) if 'br' in x.get_attribute('class')]

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
        highlighted_elements = self.__driver.find_elements(By.CSS_SELECTOR, '.highlight')

        if not highlighted_elements:
            return False

        if not self.__is_flipped:
            dest = self.__driver.find_elements(By.CSS_SELECTOR, '.black.node.selected')
        else:
            dest = self.__driver.find_elements(By.CSS_SELECTOR, '.white.node.selected')

        if dest:
            dest = dest[0].text
        else:
            return False

        try:
            self.push_move(dest)
        except ValueError:
            return False

        if self.__is_debug:
            utils.log('update_board', f'Opponent Move: {dest}')

        if dest == 'O-O':
            if not self.__is_flipped:
                self.__overwrite_element('e8', 'g8')
                self.__overwrite_element('h8', 'f8')
            else:
                self.__overwrite_element('e1', 'g1')
                self.__overwrite_element('h1', 'f1')
        elif dest == 'O-O-O':
            if not self.__is_flipped:
                self.__overwrite_element('e8', 'c8')
                self.__overwrite_element('a8', 'd8')
            else:
                self.__overwrite_element('e1', 'g1')
                self.__overwrite_element('h1', 'f1')
        else:
            if '+' in dest:
                dest = dest.replace('+', '')
            if 'x' in dest:
                dest = dest.replace('x', '')

            if len(dest) == 3:
                dest = dest[1:]
            elif len(dest) == 4:
                dest = dest[0] + dest[-2:]

            dest_num = str(self.__letters_to_numbers[dest[0]]) + dest[1]
            indices = [i for i, x in enumerate(highlighted_elements) if dest_num not in x.get_attribute('class')]
            row = self.__numbers_to_letters[int(highlighted_elements[indices[0]].get_attribute('class')[-2:-1])]
            col = highlighted_elements[indices[0]].get_attribute('class')[-1]

            src = row + col

            self.__overwrite_element(src, dest)

        return True

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

    def move(self, fen):
        self.push_move(fen)

        if fen == 'O-O-O':
            src = 'e1'
            dest = 'c1'
        elif fen == 'O-O':
            src = 'e1'
            dest = 'g1'
        elif len(fen) == 3:
            piece = self.__fen_to_name[fen[0]]
            dest = fen[1:]
            src = []

            for k, v in self.__board.items():
                if v['piece'] == piece:
                    src.append(k)

            if self.__is_debug:
                utils.log('move', f'Player Click: (Src: {src}, Dest: {dest})')

            for m in src:
                self.__move_click(m, dest)

            return
        else:
            src = fen[0:2]
            dest = fen[2:]

        if self.__is_debug:
            utils.log('move', f'Player Click: (Src: {src}, Dest: {dest})')

        self.__move_click(src, dest)

    def __move_click(self, src, dest):
        src_element, src_piece = self.__overwrite_element(src, dest)

        ac = ActionChains(self.__driver)
        ac.move_to_element(src_element)
        ac.click()

        y = self.__board[dest]['y'] - self.__board[src]['y']
        x = self.__board[dest]['x'] - self.__board[src]['x']

        ac.move_to_element_with_offset(src_element, x, y)
        ac.click()
        ac.perform()

    def __reset_board(self):
        self.__chess_lib_board = chess.Board()
        self.__board = {}
        self.__is_flipped = False

    def is_flipped(self):
        return self.__is_flipped
