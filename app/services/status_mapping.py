from app.db.enum import TrackingStatus, HighLevelStatus

INTRANSIT_STATUS = {
    TrackingStatus.NEW,
    TrackingStatus.ASSIGNED,
    TrackingStatus.VERIFIED,
    TrackingStatus.INTRANSIT,
    TrackingStatus.REJECTED,
    TrackingStatus.FAILED,
}

REACHED_STATUS = {TrackingStatus.APPROVED}


def allowed_status(high_level_status: HighLevelStatus):
    return (
        REACHED_STATUS
        if high_level_status.upper() == HighLevelStatus.REACHED
        else INTRANSIT_STATUS
    )
