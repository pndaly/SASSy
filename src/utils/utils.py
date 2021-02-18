#!/usr/bin/env python3


# +
# import(s)
# -
import logging
import logging.config
import os


# +
# constant(s)
# -
LOG_CLR_FMT = \
    '%(log_color)s%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_CSL_FMT = \
    '%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_FIL_FMT = \
    '%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG_WWW_DIR = '/var/www/SASSy/logs'
MAX_BYTES = 9223372036854775807


# +
# class: UtilsLogger() inherits from the object class
# -
# noinspection PyBroadException
class UtilsLogger(object):

    # +
    # method: __init__
    # -
    def __init__(self, name='', level='DEBUG'):

        # get arguments(s)
        self.name = name
        self.level = level

        # define some variables and initialize them
        self.__msg = None
        # self.__logconsole = f'/tmp/console-{self.__name}.log'
        self.__logdir = os.getenv("SASSY_LOGS", f"{LOG_WWW_DIR}")
        if not os.path.exists(self.__logdir) or not os.access(self.__logdir, os.W_OK):
            self.__logdir = os.getcwd()
        self.__logfile = f'{self.__logdir}/{self.__name}.log'

        # logger dictionary
        utils_logger_dictionary = {

            # logging version
            'version': 1,

            # do not disable any existing loggers
            'disable_existing_loggers': False,

            # use the same formatter for everything
            'formatters': {
                'UtilsColoredFormatter': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': LOG_CLR_FMT,
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'white,bg_red',
                    }
                },
                'UtilsConsoleFormatter': {
                    'format': LOG_CSL_FMT
                },
                'UtilsFileFormatter': {
                    'format': LOG_FIL_FMT
                }
            },

            # define file and console handlers
            'handlers': {
                'colored': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'UtilsColoredFormatter',
                    'level': self.__level,
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'UtilsConsoleFormatter',
                    'level': self.__level,
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'backupCount': 10,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'UtilsFileFormatter',
                    'filename': self.__logfile,
                    'level': self.__level,
                    'maxBytes': MAX_BYTES
                },
                #'utils': {
                    #'backupCount': 10,
                    #'class': 'logging.handlers.RotatingFileHandler',
                    #'formatter': 'UtilsFileFormatter',
                    #'filename': self.__logconsole,
                    #'level': self.__level,
                    #'maxBytes': MAX_BYTES
                #}
            },

            # make this logger use file and console handlers
            'loggers': {
                self.__name: {
                    'handlers': ['colored', 'file'],
                    'level': self.__level,
                    'propagate': True
                }
            }
        }

        # configure logger
        logging.config.dictConfig(utils_logger_dictionary)

        # get logger
        self.logger = logging.getLogger(self.__name)

    # +
    # Decorator(s)
    # -
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name=''):
        self.__name = name if (isinstance(name, str) and name.strip() != '') else os.getenv('USER')

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level=''):
        self.__level = level.upper() if \
            (isinstance(level, str) and level.strip() != '' and level.upper() in LOG_LEVELS) else LOG_LEVELS[0]
