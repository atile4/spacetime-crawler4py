def tokenize(path : str) -> list[str]:
    # list containing all resulting tokens
    tokens = []

    try:
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                # tokenize curr line

                # to account for possessive/shortened words
                line = line.lower().replace("'", "") 

                # replace special characters with blank space
                cleaned = ''.join([c if c.isalnum() and c.isascii() else ' ' for c in line])

                # add tokens in the current line to tokens list
                tokens.extend(cleaned.split())

    except:
        raise FileNotFoundError("Could not find file")

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
