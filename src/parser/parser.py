import re
from collections import defaultdict

# Case-insensitive match for "Country name: <name>"
country_re = pattern = re.compile(
    r"""^
    (?P<name>[^:]+?)\s*:                 # Country/Entity name
    \s*(?P<cq>\d+)\s*:                   # CQ zone
    \s*(?P<itu>\d+)\s*:                  # ITU zone
    \s*(?P<cont>[A-Z]{2})\s*:            # Continent (EU/AS/AF/NA/SA/OC/AN)
    \s*(?P<lat>-?\d+(?:\.\d+)?)\s*:      # Latitude  (decimal, signed)
    \s*(?P<lon>-?\d+(?:\.\d+)?)\s*:      # Longitude (decimal, signed)
    \s*(?P<utc>-?\d+(?:\.\d+)?)\s*:      # UTC offset (decimal, signed)
    \s*(?P<prefix>[A-Z0-9/]+)\s*:        # Callsign prefix (e.g., 1A)
    \s*$""",
    re.X | re.I
)

def parse_cty_dat(path):
    pattern_map = defaultdict(set)  # multimap: key -> {countries}
    exact_map = defaultdict(set)    # multimap: key -> {countries}

    current_country = None

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            m = country_re.match(line)
            if m:
                current_country = m.group(1).strip()
                continue
            # Continuation lines (keys) must start with whitespace and require a current country
            if current_country and line[:1].isspace():
                key_part = line.split(';', 1)[0]
                for tok in key_part.split(','):
                    tok = tok.strip()
                    # Drop trailing punctuation or stray commas
                    tok = tok.strip(' ,\t')
                    if tok:
                        if tok.startswith('='):
                            exact_map[tok[1:]].add(current_country)   # strip leading '='
                        else:
                            pattern_map[tok].add(current_country)
                continue

            # Anything else we ignore (malformed or unrelated lines)


    return pattern_map, exact_map

def main():
    print("main")
    
if __name__ == "__main__":
    main()