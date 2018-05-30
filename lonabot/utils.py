import re
from datetime import datetime


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

            if re.match(r'h(our)?s?', unit):
                hour += value
            elif re.match(r'm(in(ute)?s?)?', unit):
                mins += value
            elif re.match(r's(ecs?)?', unit):
                secs += value
            else:
                mins += value
                if m.group(2):
                    # Unit next to number, but invalid, so set the text
                    when[i] = m.group(2)
                else:
                    # Next wasn't a valid unit so assume it's reminder text
                    i -= 1
                break
            i += 1
        text = ' '.join(when[i:])

    delay = (hour * 60 + mins) * 60 + secs
    due = int(datetime.utcnow().timestamp() + delay) if delay else None
    return due, text
