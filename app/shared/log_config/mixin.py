from bootstrap import get_bootstrap
import logging

logger_name = get_bootstrap().config.log_info.log_name


class LogMixin:
    """Миксин для добавления логирования в классы"""
    @property
    def get_logger(self):
        """Получение логгера"""
        return logging.getLogger(logger_name)

    def log_debug(self, msg: str):
        """
        Лог уровня debug
        :param msg: сообщение для логирования
        :return:
        """
        self.get_logger.debug(msg)

    def log_info(self, msg: str):
        """
        Лог уровня info
        :param msg: сообщение для логирования
        :return:
        """
        self.get_logger.info(msg)

    def log_warning(self, msg: str):
        """
        Лог уровня info
        :param msg: сообщение для логирования
        :return:
        """
        self.get_logger.warning(msg)

    def log_error(self, msg:str, is_exp: bool = False):
        """
        Лог уровня info
        :param msg: сообщение для логирования
        :param is_exp: является ли ошибка исключением (для вывода исключения в файл)
        :return:
        """
        self.get_logger.error(msg)