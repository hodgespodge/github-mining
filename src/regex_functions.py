import re

def in_regex_list(patterns, string ):
    for pattern in patterns:

        match = re.search(pattern, string)

        if match:
            return True , pattern

    return False , None

def any_string_in_pattern(pattern, strings):
    for string in strings:
        if in_regex(pattern, string):
            return True
    return False

def in_regex(pattern, string ):
    match = re.search(pattern, string)

    if match:
        return True

    return False