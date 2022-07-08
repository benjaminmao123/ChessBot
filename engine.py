from stockfish import Stockfish


class Engine:
    def __init__(self):
        self.__engine = Stockfish(path='assets/stockfish_15_x64_avx2.exe')
        self.__board_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def update_engine(self, fen):
        self.__engine.set_fen_position(fen)

    def get_best_move(self):
        return self.__engine.get_best_move()

