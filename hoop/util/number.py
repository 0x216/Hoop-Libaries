def nth(number):
    if 4 <= number <= 20 or 24 <= number <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][number % 10 - 1]
