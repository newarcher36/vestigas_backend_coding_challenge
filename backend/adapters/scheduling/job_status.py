from enum import Enum


class JobStatus(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"