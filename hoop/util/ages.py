def format_age(age_mode, age_min, age_max, minimal=False):
    # Convert months back into years
    if age_mode == 'Y':
        if age_max:
            age_max = int((age_max - 11) / 12)
        if age_min:
            age_min = int(age_min / 12)

    elif age_mode == 'M':
        if age_min:
            age_min = int(age_min)
        if age_max:
            age_max = int(age_max)

    else:
        if age_min:
            age_min = int(age_min)
        if age_max:
            age_max = int(age_max / 12)

    if age_mode in ['Y', 'M']:
        if not minimal:
            age_mode = ('months' if age_mode == 'M' else 'years')
        else:
            age_mode = ('mo' if age_mode == 'M' else 'yo')

        if age_min and age_max:
            if not minimal:
                return '%s - %s %s' % (age_min, age_max, age_mode)
            return '%s-%s%s' % (age_min, age_max, age_mode)
        elif age_min:
            if not minimal:
                return '%s %s and above' % (age_min, age_mode)
            return '>%s%s' % (age_min, age_mode)
        elif age_max:
            if not minimal:
                return 'Up to %s %s' % (age_max, age_mode)
            return '<%s%s' % (age_max, age_mode)

    elif age_mode == 'X':
        if age_min and age_max:
            if not minimal:
                return '%s months - %s years' % (age_min, age_max)
            return '%smo-%syo' % (age_min, age_max)
        elif age_min:
            if not minimal:
                return '%s months and above' % (age_min)
            return '>%smo' % (age_min)
        elif age_max:
            if not minimal:
                return 'Up to %s years' % (age_max)
            return '<%syo' % (age_max)

    if not minimal:
        return 'All Ages'
    return ''


def check_age_ranges(age_ranges, age_min, age_max):
    if not age_ranges:
        return True

    age_min = int(age_min) if age_min else 0
    age_max = int(age_max) if age_max else 192

    for range in age_ranges:
        range_min, range_max = range.split('-')

        range_min = int(range_min)
        range_max = int(range_max)

        if range_max >= age_min and range_min <= age_max:
            return True
