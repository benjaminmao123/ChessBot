from chess_bot import ChessBot
from configparser import ConfigParser


if __name__ == '__main__':
    config = ConfigParser()
    config.optionxform = str
    config.read('assets/settings.ini')

    bot = ChessBot(config)
    bot.run()


