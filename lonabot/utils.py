import calendar
import itertools
import re
from datetime import datetime, timedelta, timezone

import pytz

from .database import TimeDelta


class NoDeltaError(ValueError):
    pass


_UNITS = {
    'y': 31536000.0,
    'mo': 2592000.0,
    'w': 604800.0,
    'd': 86400.0,
    'h': 3600.0,
    'm': 60.0,
    's': 1.0
}

# Reuse floating number regex to reduce verbosity
_F = r'(\d+(?:\.\d+)?)'

_UNIT_DELAY_PARSE = re.compile(
    fr'\s*{_F}\s*'
    r'(y(?:ea)?r?s?'
    r'|mo(?:nth)?s?'
    r'|w(?:eek)?s?'
    r'|d(?:ay)?s?'
    r'|h(?:ou)?r?s?'
    r'|m(?:in(?:ute)?)?s?'
    r'|s(?:ec(?:ond)?)?s?)'
    r'(?=\b|\d)',
    re.IGNORECASE
)

_DUE_DATE_YMD = re.compile(r'(?:(\d{4})[/-])?(\d{1,2})[/-](\d{1,2})')
_DUE_TIME = re.compile(fr'{_F}:{_F}(?::{_F})?')


def parse_when(when, time_delta: TimeDelta, utc_now):
    # Returns `due` for either `delay` or `due`.
    due, text = parse_due(when, time_delta, utc_now)
    if due:
        return due, text

    delay, text = parse_delay(when)
    if delay:
        due = int(utc_now.timestamp() + delay)
        return due, text

    return None, None


def parse_delay(when):
    iso = _parse_delay_iso(when)
    if iso:
        return iso

    delay = 0.0
    while True:
        m = _UNIT_DELAY_PARSE.match(when)
        if not m:
            break

        # TODO Find a better way to support 'mo' and 'm'
        unit = (m.group(2) or 'm').lower()
        if unit.startswith('mo'):
            unit = unit[:2]
        else:
            unit = unit[0]

        delay += float(m.group(1)) * _UNITS[unit.lower()]
        when = when[m.end():]

    # when has become text by now
    return int(delay), when.lstrip()


def _parse_due_date(part):
    """
    Parse a part of text as a date, in either DD/MM/YYYY or YYYY/MM/DD format.
    """
    m = _DUE_DATE_YMD.match(part)
    if m:
        return m.groups()


def _parse_due_time(part):
    """
    Parse a part of text as a time, only the hours being mandatory.
    """
    m = _DUE_TIME.match(part)
    if m:
        return m.groups()


def _parse_date_parts(due):
    """
    Parse the entire due text as  `(date tuple, time tuple, text)`.
    This tries first date and then time optionally, and first time
    and then date optionally (4 combinations, 8 if we consider year
    or day first in the date).

    Note that the tuples contain strings or a possibly false-y value,
    so the caller is responsible for asserting what they get.
    """
    empty = (0, 0, 0)
    parts = due.split(maxsplit=2)

    # Date then time
    date_part = _parse_due_date(parts[0])
    if date_part:
        if len(parts) == 1:
            return date_part, empty, ''

        time_part = _parse_due_time(parts[1])
        if time_part:
            return date_part, time_part, parts[2] if len(parts) > 2 else ''
        else:
            parts = due.split(maxsplit=1)
            return date_part, empty, parts[1]

    # Time then date
    time_part = _parse_due_time(parts[0])
    if time_part:
        if len(parts) == 1:
            return empty, time_part, ''

        date_part = _parse_due_date(parts[1])
        if date_part:
            return date_part, time_part, parts[2] if len(parts) > 2 else ''
        else:
            parts = due.split(maxsplit=1)
            return empty, time_part, parts[1]

    return empty, empty, due


def parse_due(due, time_delta, utc_now):
    delta = None
    try:
        try:
            d, t = due.split(maxsplit=1)
        except ValueError:
            d, t = due, ''

        if 'T' not in d:
            raise ValueError('Not parsing ISO date without T')

        d = datetime.fromisoformat(d)

        # Parsing succeeded, so set the correct text now.
        # We don't want to clobber `text` until `d` is valid.
        text = t
        day, month, year, hour, mins, sec = (
            d.day, d.month, d.year, d.hour, d.minute, d.second)

        if d.tzinfo:
            delta = d.tzinfo.utcoffset(utc_now).total_seconds()

    except (ValueError, AttributeError):
        date, time, text = _parse_date_parts(due)
        year, month, day, hour, mins, sec = (
            int(x or 0) for x in itertools.chain(date, time))

        if not any((year, month, day, hour, mins, sec)):
            return None, due

    now = utc_now

    if delta is None:
        if time_delta is None:
            raise NoDeltaError('delta was None (and due had no TZ info)')
        if time_delta.time_zone is None:
            delta = time_delta.delta
        else:
            tz = pytz.timezone(time_delta.time_zone)
            naive = datetime(
                year or now.year, month or now.month, day or now.day,
                hour, mins, sec, 0
            )
            # This gives us the correct offset with respect to DST
            delta = tz.utcoffset(naive).total_seconds()

    # Work in local time...
    now += timedelta(seconds=delta)
    due = datetime(
        year or now.year, month or now.month, day or now.day,
        hour, mins, sec, 0, now.tzinfo
    )

    if due < now:
        # If the date is specified, we will always have a month.
        # If the month is the past (and no year was specified),
        # then the only possible date is next year.
        if day and month and not year:
            if not year:
                due += timedelta(days=365)
                if calendar.isleap(due.year) and due > datetime(now.year + 1, 2, 28, 23, 59, 59, tzinfo=timezone.utc):
                    due += timedelta(days=1)
        elif not any((day, month, year)):
            due += timedelta(days=1)

    # ...but return UTC time
    return int(due.timestamp() - delta), text


def spell_digit(n):
    return ['zero', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine'][n]


def spell_ten(n):
    return ['ten', 'twenty', 'thirty', 'forty', 'fifty',
            'sixty', 'seventy', 'eighty', 'ninety'][n - 1]


def spell_number(n, allow_and=True):
    # In the range of [0..1_000_000), for now
    if n < 0:
        spelt = 'minus'
        n = -n
    else:
        spelt = ''

    add_and = False
    if n >= 1000:
        add_and = allow_and
        high, n = divmod(n, 1000)
        spelt += f' {spell_number(high, allow_and=False)} thousand'
    if n >= 100:
        add_and = allow_and
        high, n = divmod(n, 100)
        spelt += f' {spell_digit(high)} hundred'
    if n >= 20:
        if add_and:
            spelt += ' and'
            add_and = False
        high, n = divmod(n, 10)
        spelt += f' {spell_ten(high)}'
    elif n >= 10:
        if add_and:
            spelt += ' and'
            add_and = False
        spelt += ' ' + [
            'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
            'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'
        ][n - 10]
        n = 0

    if n or not spelt:
        if add_and:
            spelt += ' and'
        spelt += ' ' + spell_digit(n)

    return spelt.lstrip()


def spell_due(due, utc_now, time_delta=None, prefix=True):
    if prefix and time_delta is not None:
        # Looks like doing .utcfromtimestamp "subtracts" the +N local time…?
        if time_delta.time_zone is None:
            due = datetime.fromtimestamp(due + time_delta.delta, tz=pytz.UTC)
        else:
            due_utc = datetime.fromtimestamp(due, tz=pytz.UTC)
            due = utc_to_local(due_utc, time_delta.time_zone)

        due = due.strftime('%Y-%m-%d %H:%M:%S')
        return f'due at {due}'

    return spell_delay(int(due - utc_now.timestamp()), prefix=prefix)


def spell_delay(remaining, prefix=True):
    spelt = 'due in' if prefix else ''
    if remaining < 60:
        spelt += f' {remaining} second'
        if remaining != 1:
            spelt += 's'
        return spelt.lstrip()

    written = False
    if remaining >= 86400:
        days, remaining = divmod(remaining, 86400)
        spelt += f' {days} day'
        written = True
        if days != 1:
            spelt += 's'
    if remaining >= 3600:
        hours, remaining = divmod(remaining, 3600)
        spelt += f' {hours} hour'
        written = True
        if hours != 1:
            spelt += 's'

    mins, remaining = divmod(remaining, 60)
    if mins or not written:
        spelt += f' {mins} minute'
        if mins != 1:
            spelt += 's'

    return spelt.lstrip()


def _parse_delay_iso(when):
    try:
        when, text = re.match(r'(\S+)(.*)', when).groups()
    except AttributeError:
        return 0, when

    delay = parse_iso_duration(when)
    if delay is not None:
        return int(delay), text


def parse_iso_duration(what):
    # https://en.wikipedia.org/wiki/ISO_8601#Durations
    # Yes https://pypi.org/project/isodate/ exists.
    # Yes I'm still using my own implementation. Sorry /bin/test ! -f
    mapping = {
        'Y': 365*24*60*60,
        'M':  30*24*60*60,
        'W':   7*24*60*60,
        'D':     24*60*60
    }

    what = what.upper()
    if what[0] != 'P':
        return None  # invalid format

    result = 0
    number = ''
    what = what[1:].replace(',', '.')
    for c in what:
        if c.isdigit() or c == '.':
            number += c
        elif c == 'T':
            if number:
                return None  # T without previous unit
            else:
                mapping = {
                    'H': 60*60,
                    'M':    60,
                    'S':     1
                }
        else:
            try:
                result += float(number) * mapping[c]
                number = ''
            except ValueError:
                return None  # malformed floating point number
            except KeyError:
                return None  # unknown unit

    return result


def large_round(number, precision):
    # e.g. large_round(11, 5) -> 10
    return round(number / precision) * precision


def split_message(message, known=(
    'audio', 'document', 'video', 'voice', 'sticker', 'video_note'
)):
    """
    Split message into ``(text, media type, file_id)``.
    """
    text = message.text or message.caption or ''
    if message.photo:
        return text, 'photo', message.photo[-1].file_id
    else:
        for what in known:
            attr = getattr(message, what)
            if attr:
                return text, what, attr.file_id

    return text, None, None

def utc_to_local(utc, zone):
    tz = pytz.timezone(zone)

    # CAUTION: `astimezone` ONLY works if `utc` is NOT a naive datetime!
    return utc.astimezone(tz)
