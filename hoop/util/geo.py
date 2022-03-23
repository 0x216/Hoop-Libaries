from math import acos, cos, radians, sin


def distance(origin, destination, unit='mi'):
    # Convert all parameters into floats
    origin = (float(origin[0]), float(origin[1]))
    destination = (float(destination[0]), float(destination[1]))

    if origin == destination:
        return 0.0

    if unit == 'mi':
        multiplier = 3959
    else:
        multiplier = 6367

    return (
        multiplier * acos(
            cos(radians(origin[0])) * cos(radians(destination[0])) * cos(radians(destination[1]) - radians(origin[1])) +
            sin(radians(origin[0])) * sin(radians(destination[0]))
        )
    )


def get_postcode_district(postcode):
    # First get rid of all whitespace
    postcode = ''.join(postcode.split())

    # Now we want everything apart
    # from the final three characters
    return postcode[:-3]
