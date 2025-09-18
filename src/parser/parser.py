import re
from collections import defaultdict
from bs4 import BeautifulSoup
import requests

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

worked_states = [
    "AL",
    "AR",
    "AZ",
    "CA",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "KY",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "NC",
    "ND",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OR",
    "PA",
    "RI",
    "SC",
    "TN",
    "TX",
    "UT",
    "VA",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
    ]


def main():
    pattern_map, exact_map = parse_cty_dat("cty.dat")

    # line parser:  "10Sep 19:34 <message> ====== {<meta>}"
    line_rx = re.compile(r"""^\s*
        (?P<daymon>\d{2}[A-Za-z]{3})\s+
        (?P<time>\d{2}:\d{2})\s+
        (?P<message>.*?)\s+
        ======\s+\{(?P<meta>.*?)\}\s*$
        """, re.X)

    # meta helpers
    callsign_rx = re.compile(r"^[A-Z0-9]+", re.I)
    grid_rx = re.compile(r"\b([A-R]{2}\d{2})", re.I)  # e.g., JO33, RE68
    region_re = re.compile(r'^(\S+)\s(\S+)\s(\S+)')

    entries = []
    URL = "https://www.chris.org/cgi-bin/jt65emeA"

    html = requests.get(URL, timeout=30).text
    text = BeautifulSoup(html, "html.parser").get_text()
    lines = [line.rstrip() for line in text.splitlines()]

    for line in lines:
        m = line_rx.match(line)
        if not m:
            continue
        daymon, t, msg, meta = m.group("daymon", "time", "message", "meta")
        daymon = daymon[:2] + " " + daymon[2:]

        # parse meta ? callsign, name, grid (best-effort)
        call = (callsign_rx.search(meta).group(0) if callsign_rx.search(meta) else None)
        grid_match = grid_rx.search(meta)
        grid = grid_match.group(1) if grid_match else None

        state = None
        if call:
            m = region_re.search(meta)
            if m:
                state = m.group(3)
        if state == "xx":
            state = "";
        if state and state not in worked_states:
            print(call, grid, state)

            # if state and state != "xx"and state not in worked_states:
                # print(state)

        entries.append({
            "utc": daymon + " " + t,
            "message": msg.strip(),
            "sender": meta.strip(),
            "call": call,
            "grid": grid
        })

    # for line in entries:
        # dxcc = find_dxcc(line["call"])
        # if not dxcc:
            # dxcc = "\033[31mNone\033[0m"
        # if dxcc not in worked:
            # print(line["utc"], line["message"], line["call"], line["grid"], dxcc)

    print(f"parsed {len(entries)} lines")

if __name__ == "__main__":
    main()