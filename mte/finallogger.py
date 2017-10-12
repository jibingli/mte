# coding:utf-8

import logging.handlers
import os
import datetime


class FinalLogger(object):
    logger = None

    levels = {
        "n": logging.NOTSET,
        "d": logging.DEBUG,
        "i": logging.INFO,
        "w": logging.WARN,
        "e": logging.ERROR,
        "c": logging.CRITICAL
    }

    log_level = "d"
    logging_file_path = '/tmp/'
    log_max_byte = 10 * 1024 * 1024
    log_backup_count = 5

    @property
    def logging_file_path(self):
        return self.logging_file_path

    @logging_file_path.setter
    def logging_file_path(self, input):
        self.logging_file_path = str(input)

    @staticmethod
    def get_logger():
        if FinalLogger.logger is not None:
            return FinalLogger.logger

        FinalLogger.logger = logging.Logger(name='FinalLogger')
        log_fmt = logging.Formatter("%(levelname)s %(asctime)s %(module)s.%(funcName)s | %(message)s  ")
        # 文件保存日志
        if not os.path.exists(FinalLogger.log_dir):
            os.mkdir(FinalLogger.log_dir)
        log_file = FinalLogger.log_dir + '/mte_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        log_handler = logging.handlers.RotatingFileHandler(
            filename=log_file, maxBytes=FinalLogger.log_max_byte,
            backupCount=FinalLogger.log_backup_count)
        log_handler.setFormatter(log_fmt)
        FinalLogger.logger.addHandler(log_handler)
        FinalLogger.logger.setLevel(FinalLogger.levels.get(FinalLogger.log_level))

        # 控制台打印日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(FinalLogger.levels.get(FinalLogger.log_level))
        console_handler.setFormatter(log_fmt)
        FinalLogger.logger.addHandler(console_handler)

        return FinalLogger.logger


logger = FinalLogger.get_logger()

if __name__ == "__main__":
    logger = FinalLogger.get_logger()
    logger.debug("this is a debug msg!")
    logger.info("this is a info msg!")
    logger.warn("this is a warn msg!")
    logger.error("this is a error msg!")
    logger.critical("this is a critical msg!")
    dic = {"key": '中文'}
    import json

    logger.info("中文显示 %s" % json.dumps(dic, encoding='utf-8', ensure_ascii=False))
