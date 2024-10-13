import os

from bot import HappyLittleBot
from logger import setup_logger


if __name__ == '__main__':
    setup_logger()
    bot = HappyLittleBot()
    bot.run(os.getenv('TOKEN'))
