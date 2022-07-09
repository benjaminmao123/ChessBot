from stockfish import Stockfish


class Engine:
    def __init__(self, config):
        params = {}

        for option in config.options('Engine'):
            if option == 'depth' or option == 'best_move_time_limit':
                continue

            value = config.get('Engine', option)

            if value == 'true' or value == 'false':
                params[option] = config.getboolean('Engine', option)
            else:
                params[option] = config.getint('Engine', option)

        self.__engine = Stockfish(path='assets/stockfish_15_x64_avx2.exe',
                                  depth=config.getint('Engine', 'depth'),
                                  parameters=params)

    def update_engine(self, fen):
        self.__engine.set_fen_position(fen)

    def get_best_move(self, time=500):
        return self.__engine.get_best_move_time(time)
