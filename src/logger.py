# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import logging
import os
import sys
from datetime import datetime
import colorlog


def setup_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    time_format = "%H:%M:%S"
    log_file = os.path.join(log_dir, f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log")

    logger = logging.getLogger("finam_app")
    logger.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d: %(message)s',
        datefmt=time_format
    )

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_formatter = colorlog.ColoredFormatter(
        '%(light_blue)s[%(asctime)s] %(log_color)s[%(levelname)s]%(reset)s %(cyan)s(%(filename)s:%(lineno)d) %(reset)s%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red,bg_white',
        },
        reset=True,
        style='%',
        datefmt=time_format
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


Logger = setup_logger()