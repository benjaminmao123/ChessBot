import chess


class Parser:
    letters_to_numbers = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6', 'g': '7', 'h': '8'}
    numbers_to_letters = dict((v, k) for k, v in letters_to_numbers.items())

    fen_to_name_white = {'R': 'wr', 'N': 'wn', 'B': 'wb', 'Q': 'wq', 'K': 'wk'}
    fen_to_name_black = {'R': 'br', 'N': 'bn', 'B': 'bb', 'Q': 'bq', 'K': 'bk'}
    fen_to_name_black_promo = {'r': 'br', 'n': 'bn', 'b': 'bb', 'q': 'bq', 'k': 'bk'}
    name_to_fen_white = dict((v, k) for k, v in fen_to_name_white.items())
    name_to_fen_black = dict((v, k) for k, v in fen_to_name_black.items())

    @staticmethod
    def parse_move_from_site(san, h_elements, turn):
        is_promotion = False
        promo_piece_name = None

        san = san.replace('x', '')
        san = san.replace('+', '')

        if san == 'O-O':
            if turn:
                return {'squares': [('e1', 'g1'), ('h1', 'f1')], 'promotion': (is_promotion, promo_piece_name)}
            else:
                return {'squares': [('e8', 'g8'), ('h8', 'f8')], 'promotion': (is_promotion, promo_piece_name)}
        elif san == 'O-O-O':
            if turn:
                return {'squares': [('e1', 'c1'), ('a1', 'd1')], 'promotion': (is_promotion, promo_piece_name)}
            else:
                return {'squares': [('e8', 'c8'), ('a8', 'd8')], 'promotion': (is_promotion, promo_piece_name)}

        if '=' in san:
            is_promotion = True

        san = san.replace('=', '')

        if not is_promotion:
            dest_square_num = Parser.letters_to_numbers[san[-2:-1]] + san[-1]
            dest_square = san[-2:]
        else:
            dest_square_num = Parser.letters_to_numbers[san[-3:-2]] + san[-2]
            dest_square = san[-3:-1]

            if turn:
                promo_piece_name = Parser.fen_to_name_white[san[-1]]
            else:
                promo_piece_name = Parser.fen_to_name_black[san[-1]]

        name = None

        for e in h_elements:
            name = e.get_attribute('class')

            if dest_square_num not in name:
                break

        src_square = Parser.numbers_to_letters[name[-2:-1]] + name[-1]

        return {'squares': [(src_square, dest_square)], 'promotion': (is_promotion, promo_piece_name)}

    @staticmethod
    def parse_move_from_engine(san, board):
        san = san.replace('x', '')
        san = san.replace('+', '')

        is_promotion = False
        promo_piece_name = None

        if san == 'O-O' or san == 'e8g8' or san == 'e1g1':
            if board.is_flipped():
                return {'squares': [('e8', 'g8'), ('h8', 'f8')], 'promotion': (is_promotion, promo_piece_name)}
            else:
                return {'squares': [('e1', 'g1'), ('h1', 'f1')], 'promotion': (is_promotion, promo_piece_name)}
        elif san == 'O-O-O' or san == 'e8c8' or san == 'e1c1':
            if board.is_flipped():
                return {'squares': [('e8', 'c8'), ('a8', 'd8')], 'promotion': (is_promotion, promo_piece_name)}
            else:
                return {'squares': [('e1', 'c1'), ('a1', 'd1')], 'promotion': (is_promotion, promo_piece_name)}

        if len(san) == 3:
            if board.is_flipped():
                piece_name = Parser.fen_to_name_black_promo[san[-1]]
            else:
                piece_name = Parser.fen_to_name_white[san[-1]]

            src_square = None
            dest_square = san[-2:]

            potential_squares = board.get_all_pieces_with_name(piece_name)

            for square in potential_squares:
                move = chess.Move.from_uci(square + dest_square)

                if board.is_legal_move(move):
                    src_square = square
                    break
        elif len(san) == 4:
            src_square = san[0:2]
            dest_square = san[2:]
        else:
            if board.is_flipped():
                promo_piece_name = Parser.fen_to_name_black[san[-1]]
            else:
                promo_piece_name = Parser.fen_to_name_white[san[-1].upper()]

            is_promotion = True

            src_square = san[0:2]
            dest_square = san[2:-1]

        return {'squares': [(src_square, dest_square)], 'promotion': (is_promotion, promo_piece_name)}
