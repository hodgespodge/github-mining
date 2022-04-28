import re

def in_regex_list(patterns, string ):
    for pattern in patterns:

        match = re.search(pattern, string)

        if match:
            return True , pattern

    return False , None

def in_regex(pattern, string ):
    match = re.search(pattern, string)

    if match:
        return True

    return False