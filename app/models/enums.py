from enum import IntEnum


class MeetingStatus(IntEnum):
    CANCELED = 0
    SCHEDULED = 1
    COMPLETED = 2


class MeetingType(IntEnum):
    IN_PERSON = 0
    ONLINE = 1
    HYBRID = 2


class RoomStatus(IntEnum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class UserRole(IntEnum):
    USER = 0
    ADMIN = 1