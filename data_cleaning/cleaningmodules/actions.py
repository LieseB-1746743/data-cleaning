from enum import Enum


class OnOutlierDetect(Enum):
    FLAG = 1
    SET_NULL = 2
    REMOVE_ROW = 3
    IGNORE = 4


class OnDuplicateDetect(Enum):
    FLAG_ALL = 1
    FLAG_EXCEPT_FIRST = 5
    REMOVE_ALL = 2
    REMOVE_EXCEPT_FIRST = 3
    IGNORE = 4


class OnNullValue(Enum):
    FLAG = 1
    REMOVE_ROW = 2
    IGNORE = 3


class OnFutureDate(Enum):
    FLAG = 1
    SET_NULL = 2
    REMOVE_ROW = 3
    IGNORE = 4


class OnForeignKeyViolation(Enum):
    FLAG = 1
    REMOVE_ROW = 2
    IGNORE = 3


class OnDenialConstraintViolation(Enum):
    FLAG = 1
    REMOVE_ROW = 2
    IGNORE = 3


class OnFunctionalDependencyViolation(Enum):
    FLAG = 1
    REMOVE_ROW = 2
    IGNORE = 3
