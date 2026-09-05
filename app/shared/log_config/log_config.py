from logging import getLogger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
from bootstrap import get_bootstrap
from .filters import JsonFormatter, InfoOrDownFilter

log_info = get_bootstrap().config.log_info

app_logger = getLogger('app_logger')
app_logger.setLevel(log_info.base_log)

console_format = Formatter(
    '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d\n'
    'Message: %(message)s'
)
error_file_format = JsonFormatter()
info_file_format = JsonFormatter()

console_handler = StreamHandler()
console_handler.setFormatter(console_format)
console_handler.setLevel(log_info.base_log)

file_error_handler = RotatingFileHandler(
    filename='log-error.json',
    mode='a',
    maxBytes=1048576,
    backupCount=10,
)
file_error_handler.setFormatter(error_file_format)
file_error_handler.setLevel(log_info.error_file_log)

file_info_handler = RotatingFileHandler(
    filename='log-info.json',
    mode='a',
    maxBytes=1048576,
    backupCount=10
)
file_info_handler.setFormatter(info_file_format)
file_info_handler.addFilter(InfoOrDownFilter)
file_info_handler.setLevel(log_info.info_file_log)

app_logger.addHandler(console_handler)
app_logger.addHandler(file_info_handler)
app_logger.addHandler(file_error_handler)