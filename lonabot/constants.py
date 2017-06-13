import re
from datetime import timedelta


MAX_REMINDERS = 10
MAX_DATA_PER_REMINDER_BYTES = 256
INLINE_REMINDER_LIFE = timedelta(seconds=30)

REMINDIN_RE = re.compile(r'''
^
(?:  # First option

    (                # # MATCH 1: 'hh:mm:ss' or 'mm:ss'
        \d+          # Minutes or hours
        \s*:\s*      # ':'
        \d+          # Seconds or minutes
        (?:
            \s*:\s*  # ':'
            \d+      # Seconds, then the others are hours:minutes
        )?
    )

)
|
(?:  # Second option

    (                # # # MATCH 2: 'uu' for "units"
        \d+          # Which are a few digits
        (?:
            [,.]\d+  # Possibly capture a value after the decimal point
        )?
    )
    \s*              # Some people like to separate units from the number

    (                # # # MATCH 3: '(d|h|m|s).*' for days, hours, mins, secs
        d(?:ays?)?         # Either 'd', 'day' or 'days'
        |                  # or
        h(?:ours?)?        # Either 'h', 'hour' or 'hours'
        |                  # or
        m(?:in(?:ute)?s?)? # Either 'm', 'min', 'mins', 'minute' or 'minutes'
        |                  # or
        s(?:ec(?:ond)?s?)? # Either 's', 'sec', 'secs', 'second' or 'seconds'
    )?

)\b''', re.IGNORECASE | re.VERBOSE)


REMINDAT_RE = re.compile(r'''
^
(?:  # First option

    (                 # # MATCH 1: 'hh' or 'hh:mm' or 'hh:mm:ss'
        \d+           # Hours
        (?:
            :\d+      # Possibly minutes
            (?:
                :\d+  # Possibly seconds
            )?
        )?
    )
    \s*               # Some people like to separate am/pm from the time

    (?:               # Don't capture the whole am/pm stuff
        (?:           # Don't capture the p|a options

            (p)       # # MATCH 2: Only capture 'p', because that's when +12h
            |         # Either 'p' or
            a         # 'a'

        )
        m        # It is either 'am' or 'pm'
    )?

)\b''', re.IGNORECASE | re.VERBOSE)