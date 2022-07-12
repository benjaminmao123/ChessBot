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

        self.__config = config
        self.__engine = Stockfish(path=config['Path']['stockfish'],
                                  depth=config.getint('Engine', 'depth'),
                                  parameters=params)

    def update_fen(self, fen):
        self.__engine.set_fen_position(fen)

    def get_best_move(self, time=0):
        if time == 0:
            return self.__engine.get_best_move()

        return self.__engine.get_best_move_time(time)
