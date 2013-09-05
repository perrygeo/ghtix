import re

CONVERT_TO_HOURS = {
    'hours': 1,
    'hour': 1,
    'hrs': 1,
    'hr': 1,
    'days': 8,
    'day': 8,
    'week': 40,
    'weeks': 40,
    'wk': 40,
    'wks': 40,
}

def parse_hours_from_title(title):
    """
    [1hr] or [ 8 weeks ] but not [8.2 days] and not [8 weeks approx]
    """
    regex = re.compile(".*\[\s*(\d+)\s*(\w+)\s*\]")
    r = regex.search(title)
    if r:
        val, units = r.groups()
        val = int(val)
    else:
        val = 8
        units = "hours"

    hours = val * CONVERT_TO_HOURS[units]
    return hours
