"""
Birthday markup stuff.
"""
import calendar
import itertools


_EMPTY_BUTTON = {
    'text': '\u2063',
    'callback_data': '-'
}


def reshape(columns, array):
    """
    Reshape an array into a matrix with `columns` columns.
    """
    it = iter(array)
    return [[x for x in itertools.islice(it, columns)]
            for _ in range((len(array) + columns - 1) // columns)]


def get_month_button(month, text=None):
    """
    Get the button corresponding to the given month.

    If no `text` is given, the name of the month in English will be used.
    """
    if month < 1:
        month += 12
    elif month > 12:
        month -= 12

    return {
        'text': text or calendar.month_name[month],
        'callback_data': f'm{month:02}'
    }


def get_day_button(month, day):
    """
    Get the button corresponding to the given month's day.
    """
    if 0 < day <= calendar.monthrange(2000, month)[1]:
        return {
            'text': f'{day}',
            'callback_data': f'm{month:02}d{day:02}'
        }
    else:
        return _EMPTY_BUTTON


# reply_markup for selecting a month
MONTH_MARKUP = {
    'inline_keyboard':
        reshape(3, [get_month_button(m) for m in range(1, 13)])
}

# reply_markup for selecting a month's day
MONTH_DAY_MARKUP = [
    reshape(7, [get_day_button(m, d) for d in range(1, 32)])
    for m in range(1, 13)
]

for m, day_buttons in enumerate(MONTH_DAY_MARKUP, start=1):
    day_buttons.insert(0, [{
        'text': calendar.month_name[m],
        'callback_data': 'y'
    }])
    day_buttons[-1].insert(0, get_month_button(m - 1, '<<'))
    day_buttons[-1].append(_EMPTY_BUTTON)
    day_buttons[-1].append(_EMPTY_BUTTON)
    day_buttons[-1].append(get_month_button(m + 1, '>>'))

MONTH_DAY_MARKUP = [{'inline_keyboard': x} for x in MONTH_DAY_MARKUP]
