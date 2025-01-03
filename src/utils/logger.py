import logging
import os
import time

basepath = os.path.dirname(__file__)


# with date --> new log file each day
# Se añade un timestamp para tener un nuevo logger cada día
def get_logger() -> logging.Logger:
    """
    Se inicializa un logger para hacer print de mensajes en un archivo log.

    Returns
    -------
    logging.Logger
        Objeto logger.
    """
    log_path = os.path.join("logs")
    error_log_filename = os.path.join(
        log_path, time.strftime("%Y%m%d_") + "error_logs.log"
    )
    all_log_filename = os.path.join(log_path, time.strftime("%Y%m%d_") + "all_logs.log")

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Se defininen los parámetros a mostrar y el formato
    mformat = (
        "%(asctime)s | %(name)s | %(levelname)-5s | %(filename)-22s |"
        " @function %(funcName)-15s | line %(lineno)-4s | %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M%S"

    # Se crea un logger
    logger = logging.getLogger(name="logger")
    logger.setLevel(logging.DEBUG)

    # Se crea un "console handler" y se define el nivel de información
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(mformat, datefmt=datefmt))
    logger.addHandler(handler)

    # Se crea un "error file handler" y se define el nivel de error
    fileHandler = logging.FileHandler(filename=error_log_filename)
    fileHandler.setFormatter(logging.Formatter(mformat, datefmt=datefmt))
    fileHandler.setLevel(level=logging.ERROR)

    logger.addHandler(fileHandler)

    # Se crea un "debuf file handler" y se define el nivel de debug
    fileHandler = logging.FileHandler(filename=all_log_filename)
    fileHandler.setFormatter(logging.Formatter(mformat, datefmt=datefmt))
    fileHandler.setLevel(level=logging.INFO)

    logger.addHandler(fileHandler)

    return logger


logger_all = get_logger()
