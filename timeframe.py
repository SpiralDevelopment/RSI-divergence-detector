from enum import Enum


class TimeFrame(Enum):
    ONE_MIN = 1, "1m"
    FIFTEEN_MIN = 15, "15m"
    TWENTY_MIN = 20, "20m"
    THIRTY_MIN = 30, "30m"
    ONE_HOUR = 60, "1h"
    TWO_HOURS = 120, "2h"
    THREE_HOURS = 180, "3h"
    FOUR_HOURS = 240, "4h"
    SIX_HOURS = 360, "6h"
    EIGHT_HOURS = 480, "8h"
    NINE_HOURS = 520, "9h"
    TWELVE_HOURS = 720, "12h"
    FIFTEEN_HOURS = 900, "15h"
    EIGHTEEN_HOURS = 1080, "18h"
    ONE_DAY = 1440, "1d"

    @staticmethod
    def from_str(time_frame):
        time_frame = time_frame.lower()

        if time_frame == '1m':
            return TimeFrame.ONE_MIN
        elif time_frame == '15m':
            return TimeFrame.FIFTEEN_MIN
        elif time_frame == '20m':
            return TimeFrame.TWENTY_MIN
        elif time_frame == '30m':
            return TimeFrame.THIRTY_MIN
        elif time_frame == '1h':
            return TimeFrame.ONE_HOUR
        elif time_frame == '2h':
            return TimeFrame.TWO_HOURS
        elif time_frame == '3h':
            return TimeFrame.THREE_HOURS
        elif time_frame == '4h':
            return TimeFrame.FOUR_HOURS
        elif time_frame == '6h':
            return TimeFrame.SIX_HOURS
        elif time_frame == '8h':
            return TimeFrame.EIGHT_HOURS
        elif time_frame == '9h':
            return TimeFrame.NINE_HOURS
        elif time_frame == '12h':
            return TimeFrame.TWELVE_HOURS
        elif time_frame == '15h':
            return TimeFrame.FIFTEEN_HOURS
        elif time_frame == '18h':
            return TimeFrame.EIGHTEEN_HOURS
        elif time_frame == '1d':
            return TimeFrame.ONE_DAY
