import re
import requests

url = "https://www.chris.org/cgi-bin/jt65emeA"

# Example line:
# 04Nov 19:11 IV3VEA Ciao Roberto can you try QSO on 120? ====== {OM4CW/1X18H/750 Vlado xx JN88un }
line_re = re.compile(
    r"""
    ^\s*
    (?P<date>\d{2}[A-Za-z]{3})      # e.g., 04Nov
    \s+
    (?P<utc>\d{2}:\d{2})            # e.g., 18:53
    \s+
    (?P<message>.*?)                # free text
    \s*\{\s*
    (?P<meta>[^}]+)                 # inside {...}
    \s*\}\s*$
    """,
    re.VERBOSE,
)


response = requests.get(url)
response.raise_for_status()

for line in response.text.splitlines():
    line = line.strip()
    if not line:
        continue
    m = line_re.match(line)
    if not m:
        continue  # skip lines not matching pattern
    print(line)
