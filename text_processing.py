def tokenize(raw_text : str) -> list[str]:
    # to account for possessive/shortened words
    raw_text = raw_text.lower().replace("'", "") 

    # remove special characters
    cleaned = ''.join([c if c.isalnum() and c.isascii() else ' ' for c in raw_text])
    tokens = cleaned.split()

    return tokens


def computeWordFrequencies(tokens : list[str]) -> dict[str, int] :
    # resulting freq map
    result = {}

    # add tokens to frequency map
    for token in tokens:
        result[token] = result.get(token, 0) + 1

    # sort dictionary by value desc and alphabetically
    result = dict(sorted(result.items(), key=lambda item: (-item[1], item[0])))

    return result
