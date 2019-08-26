import sys
import os
import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30
# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class LoggerInit:
    @staticmethod
    def init(level=logging.INFO, filemode=None):

        logger = logging.getLogger()
        logger.setLevel(level=level)

        if filemode is not None:
            print(sys.modules['__main__'])
            filename = "logs/%s.log" % os.path.basename(sys.argv[0].rstrip('.py'))
            print("log file: %s" % filename)

            if not os.path.exists("logs"):
                os.mkdir('logs')

            if not os.path.exists(filename):
                open(filename, 'w').close()

            file_handler = logging.FileHandler(filename, mode=filemode)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(
                '%(process)d %(asctime)s %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))
            logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter(
            '%(process)d %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))

        logger.addHandler(console_handler)


