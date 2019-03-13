import calendar
import re
from datetime import datetime, timedelta, timezone

_UNITS = {
    'y': 31536000.0,
    'w': 604800.0,
    'd': 86400.0,
    'h': 3600.0,
    'm': 60.0,
    's': 1.0
}

_DELAY_PARSE = re.compile(r'(\d+):(\d+)(?::(\d+))?')
_UNIT_DELAY_PARSE = re.compile(r'\d+[ywdhms]?', re.IGNORECASE)

_DUE_PARSE_FWD = re.compile(r'''
    (?:
        (\d{1,2})       # day
        (?:
            [/-](\d{1,2})  # month
            (?:     # year
                [/-](\d{4})
            )?
        )?
        \s+
    )?
    (\d+)        # hours
    (?::(\d+))?  # minutes
    (?::(\d+))?  # seconds''', re.VERBOSE)

# Darn you, tan
_DUE_PARSE_REV = re.compile(r'''
    (?:
        (\d{4})       # year
        (?:
            [/-](\d{1,2})  # month
            (?:     # day
                [/-](\d{1,2})
            )?
        )?
        \s+
    )?
    (\d+)        # hours
    (?::(\d+))?  # minutes
    (?::(\d+))?  # seconds''', re.VERBOSE)

# Forward, DD/MM/YYYY
_DAY_PARSE_FWD = re.compile(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?')
# Backward, YYYY/MM/DD
_DAY_PARSE_REV = re.compile(r'(\d{4})[/-](\d{1,2})(?:[/-](\d{1,2}))?')


def parse_delay(when):
    m = _DELAY_PARSE.match(when)
    if m:
        text = when[m.end():]
        hour = int(m.group(1))
        mins = int(m.group(2))
        secs = int(m.group(3) or 0)
        delay = (hour * 60 + mins) * 60 + secs
    else:
        try:
            when, text = re.match(r'(\S+)(.*)', when).groups()
        except AttributeError:
            return 0, when

        delay = parse_iso_duration(when)
        if delay is not None:
            return int(delay), text
        else:
            delay = 0.0

        while True:
            m = _UNIT_DELAY_PARSE.match(when)
            if not m:
                break

            step = m.group(0)
            if step[-1].isdigit():
                unit = 'm'
            else:
                unit = step[-1].lower()
                step = step[:-1]

            delay += int(step) * _UNITS[unit]
            when = when[m.end():]

    return int(delay), text


def parse_due(due, delta):
    try:
        try:
            d, t = due.split(maxsplit=1)
        except ValueError:
            d, t = due, ''

        d = datetime.fromisoformat(d)

        # Parsing succeeded, so set the correct text now.
        # We don't want to clobber `text` until `d` is valid.
        text = t
        day, month, year, hour, mins, sec = (
            d.day, d.month, d.year, d.hour, d.minute, d.second)

        if d.tzinfo:
            delta = d.tzinfo.utcoffset(
                datetime.now(timezone.utc)).total_seconds()

    except (ValueError, AttributeError):
        def get_parts():
            # We could return itertools.chain(iter1, repeat three 0's),
            # but the lists are only going to be six items long anyway.
            m = _DAY_PARSE_FWD.match(due)
            if m:
                return m.end(), [int(x or 0) for x in m.groups()] + [0, 0, 0]

            m = _DAY_PARSE_REV.match(due)
            if m:
                return m.end(), [int(x or 0) for x in reversed(m.groups())] + [0, 0, 0]

            m = _DUE_PARSE_FWD.match(due)
            if m:
                return m.end(), [int(x or 0) for x in m.groups()]

            m = _DUE_PARSE_REV.match(due)
            if m:
                res = [int(x or 0) for x in m.groups()]
                res[0:3] = reversed(res[0:3])
                return m.end(), res

            return None, None

        end, parts = get_parts()
        if end is None:
            return None, due

        day, month, year, hour, mins, sec = parts
        text = due[end:]

    if delta is None:
        raise TypeError('delta was None (and due had no TZ info)')

    # Work in local time...
    now = datetime.utcnow() + timedelta(seconds=delta)
    due = datetime(
        year or now.year, month or now.month, day or now.day,
        hour, mins, sec, 0, now.tzinfo
    )

    if due < now:
        # Reasoning: if the user passed a day but the due time
        # is below the current time, we assume they meant for
        # the next month. If no month was specified, then only
        # hours were given, so it might be for the next day.
        days_in_month = calendar.monthrange(due.year, due.month)[1]
        due += timedelta(days=days_in_month if day else 1)

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


def spell_due(due, utc_delta=None, prefix=True):
    if prefix and utc_delta is not None:
        # Looks like doing .utcfromtimestamp "subtracts" the +N local time…?
        due = datetime.fromtimestamp(due + utc_delta)
        due = due.strftime('%d/%m/%Y %H:%M:%S')
        return f'due to {due}'

    return spell_delay(int(due - datetime.utcnow().timestamp()), prefix=prefix)


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
