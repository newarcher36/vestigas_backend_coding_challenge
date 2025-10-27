from enum import Enum


class StatsFields(str, Enum):
    FETCHED = "fetched"
    TRANSFORMED = "transformed"
    ERRORS = "errors"
    STORED = "stored"