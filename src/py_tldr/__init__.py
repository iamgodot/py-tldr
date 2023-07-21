from logging.config import dictConfig
from os import environ

from .core import cli
from .page import PageCache, PageFinder, PageFormatter

__version__ = "0.9.0"


logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in func `%(funcName)s` by logger `%(name)s`: %(message)s",  # NOQA
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler"
            if environ.get("TLDR_DEBUG")
            else "logging.NullHandler",
            "formatter": "default",
        }
    },
    "loggers": {
        "py_tldr": {
            "level": "DEBUG",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}
dictConfig(logging_config)
