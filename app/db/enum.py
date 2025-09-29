from enum import Enum


class TrackingStatus(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    VERIFIED = "VERIFIED"
    INTRANSIT = "IN_TRANSIT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.strip().upper().replace(" ", "_")
            for member in cls:
                if member.value == value:
                    return member


class HighLevelStatus(str, Enum):
    INTRANSIT = "IN_TRANSIT"
    REACHED = "REACHED"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.strip().upper().replace(" ", "_")
            for member in cls:
                if member.value == value:
                    return member
