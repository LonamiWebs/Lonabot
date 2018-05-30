import re
from datetime import datetime, timedelta


def parse_delay(when):
    hour = mins = secs = 0
    m = re.match(r'(\d+):(\d+)(?::(\d+))?', when)
    if m:
        hour = int(m.group(1))
        mins = int(m.group(2))
        secs = int(m.group(3) or 0)
        text = when[m.end():]
    else:
        # Try matching integers + possible units
        when = when.split() + ['']
        i = 0
        while i < len(when):
            m = re.match(r'(\d+)(.+)?', when[i])
            if not m:
                break
            value = int(m.group(1))
            unit = m.group(2)
            if not unit:
                i += 1
                unit = when[i]

            if re.match(r'h(our)?s?$', unit):
                hour += value
            elif re.match(r'm(in(ute)?s?)?$', unit):
                mins += value
            elif re.match(r's(ecs?)?$', unit):
                secs += value
            else:
                mins += value
                if m.group(2):
                    # Unit next to number, but invalid, so set the text
                    when[i] = m.group(2)
                # else next wasn't a valid unit so assume it's reminder text
                break
            i += 1
        text = ' '.join(when[i:-1])

    delay = (hour * 60 + mins) * 60 + secs
    due = int(datetime.utcnow().timestamp() + delay) if delay else None
    return due, text


def parse_due(due, delta):
    m = re.match(r'(\d+)(?::(\d+))?(?::(\d+))?', due)
    if not m:
        return None, due

    hour = int(m.group(1))
    mins = int(m.group(2) or 0)
    secs = int(m.group(3) or 0)
    text = due[m.end():]
    now = datetime.utcnow() + timedelta(seconds=delta)  # Work in local time
    due = datetime(
        now.year, now.month, now.day, hour, mins, secs, 0, now.tzinfo)

    if due < now:
        due += timedelta(days=1)

    # But return UTC time
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


def spell_due(due, utc_delta):
    if utc_delta is not None:
        # Looks like doing .utcfromtimestamp "subtracts" the +N local time…?
        due = datetime.fromtimestamp(due + utc_delta)
        return f'due to {due}'

    spelt = 'due in'
    remaining = int(due - datetime.utcnow().timestamp())
    print(remaining)
    if remaining < 60:
        spelt += f' {remaining} second'
        if remaining > 1:
            spelt += 's'
        return spelt
    if remaining >= 86400:
        days, remaining = divmod(remaining, 86400)
        spelt += f' {days} day'
        if days > 1:
            spelt += 's'
    if remaining >= 3600:
        hours, remaining = divmod(remaining, 3600)
        spelt += f' {hours} hour'
        if hours > 1:
            spelt += 's'
    mins, remaining = divmod(remaining, 60)
    spelt += f' {mins} minute'
    if mins > 1:
        spelt += 's'
    return spelt


def large_round(number, precision):
    # e.g. large_round(11, 5) -> 10
    return round(number / precision) * precision
