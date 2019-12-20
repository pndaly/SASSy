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
LOGGER_COLORED_FORMAT = '%(log_color)s%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s ' \
                              'line:%(lineno)-5d Message: %(message)s'
LOGGER_CONSOLE_FORMAT = '%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s ' \
                              'line:%(lineno)-5d Message: %(message)s'
LOGGER_FILE_FORMAT = '%(asctime)-20s %(levelname)-9s %(name)-15s %(filename)-15s %(funcName)-15s ' \
                           'line:%(lineno)-5d PID:%(process)-6d Message: %(message)s'

MAX_BYTES = 9223372036854775807


# +
# class: UtilsLogger() inherits from the object class
# -
class UtilsLogger(object):

    # +
    # method: __init__
    # -
    def __init__(self, name=''):
        """
            :param name: name of logger
            :return: None or object representing the logger
        """

        # get arguments(s)
        self.name = name

        # define some variables and initialize them
        self.__msg = None

        # logger dictionary
        logname = '{}'.format(self.__name)
        try:
            logfile = '{}/{}.log'.format(os.getenv("SASSY_LOGS"))
        except:
            logfile = '{}/{}.log'.format(os.getcwd(), logname)
        logconsole = '/tmp/console-{}.log'.format(logname)

        utils_logger_dictionary = {

            # logging version
            'version': 1,

            # do not disable any existing loggers
            'disable_existing_loggers': False,

            # use the same formatter for everything
            'formatters': {
                'UtilsColoredFormatter': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': LOGGER_COLORED_FORMAT,
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'white,bg_red',
                    }
                },
                'UtilsConsoleFormatter': {
                    'format': LOGGER_CONSOLE_FORMAT
                },
                'UtilsFileFormatter': {
                    'format': LOGGER_FILE_FORMAT
                }
            },

            # define file and console handlers
            'handlers': {
                'colored': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'UtilsColoredFormatter',
                    'level': 'DEBUG',
                    # 'stream': 'ext://sys.stdout'
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'UtilsConsoleFormatter',
                    'level': 'DEBUG',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'backupCount': 10,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'UtilsFileFormatter',
                    'filename': logfile,
                    'level': 'DEBUG',
                    'maxBytes': MAX_BYTES
                },
                'utils': {
                    'backupCount': 10,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'UtilsFileFormatter',
                    'filename': logconsole,
                    'level': 'DEBUG',
                    'maxBytes': MAX_BYTES
                }
            },

            # make this logger use file and console handlers
            'loggers': {
                logname: {
                    'handlers': ['colored', 'file', 'utils'],
                    'level': 'DEBUG',
                    'propagate': True
                }
            }
        }

        # configure logger
        logging.config.dictConfig(utils_logger_dictionary)

        # get logger
        self.logger = logging.getLogger(logname)

    # +
    # Decorator(s)
    # -
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name=''):
        self.__name = name if (isinstance(name, str) and name.strip() != '') else os.getenv('USER')
