# coding:utf-8
import os
import logging
import datetime

MTE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def config_logger():
    logger = logging.getLogger(logger_config.logger_name)
    logger.propagate = False
    logger.setLevel(logger_config.logging_level)
    logger.handlers = []

    # 文件保存日志
    file_handler = logging.FileHandler(logger_config.logging_file, mode="w")
    file_handler.setLevel(logger_config.logging_level)
    formatter = logging.Formatter(logger_config.logging_formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台打印日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_config.logging_level)
    formatter = logging.Formatter(logger_config.logging_formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class Config(object):
    _logger_name = "MTE"
    _logging_level = logging.DEBUG
    _logging_file_path = MTE_ROOT
    _logging_formatter = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d | %(message)s"
    _logging_file = os.path.join(_logging_file_path, "MTE_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log')

    def __str__(self):
        return ""

    @property
    def logger_name(self):
        return self._logger_name

    @logger_name.setter
    def logger_name(self, input):
        self._logger_name = str(input)
        config_logger()

    @property
    def logging_level(self):
        return self._logging_level

    @logging_level.setter
    def logging_level(self, input):
        logging_levels = {"CRITICAL": logging.CRITICAL,
                          "ERROR": logging.ERROR,
                          "WARNING": logging.WARN,
                          "WARN": logging.WARN,
                          "INFO": logging.INFO,
                          "DEBUG": logging.DEBUG,
                          logging.CRITICAL: logging.CRITICAL,
                          logging.ERROR: logging.ERROR,
                          logging.WARN: logging.WARN,
                          logging.INFO: logging.INFO,
                          logging.DEBUG: logging.DEBUG,}

        if input in logging_levels:
            self._logging_level = logging_levels[input]
        elif isinstance(input, str) and input.upper() in logging_levels:
            self._logging_level = logging_levels[input.upper()]
        else:
            raise ValueError("Invalid logging level %s" % input)
        config_logger()

    @property
    def logging_file_path(self):
        return self._logging_file_path

    @logging_file_path.setter
    def logging_file_path(self, input):
        self._logging_file_path = str(input)
        self._logging_file = os.path.join(self._logging_file_path,
                                          "MTE_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log')
        config_logger()

    @property
    def logging_formatter(self):
        return self._logging_formatter

    @logging_formatter.setter
    def logging_formatter(self, input):
        self._logging_formatter = str(input)
        config_logger()

    @property
    def logging_file(self):
        return self._logging_file


logger_config = Config()
