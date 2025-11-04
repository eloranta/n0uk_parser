import re
import requests
from bs4 import BeautifulSoup

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

mailto_re = re.compile(
    r"^javascript:mailto\('([^']+)','([^']+)','([^']*)'\)\s*$",
    re.IGNORECASE
)

# 6-char Maidenhead locator
locator_re = re.compile(r"^[A-Za-z]{2}\d{2}[A-Za-z]{2}$")

def fetch_text(url: str) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    # Keep as-is; this page can be plain text with embedded HTML fragments
    return r.text.replace("\r\n", "\n").replace("\r", "\n")

def parse_email_from_href(href: str | None) -> str | None:
    if not href:
        return None
    m = mailto_re.match(href.strip())
    if not m:
        return None
    user, domain, extra = m.groups()
    # Some sites split domain and TLD; here domain may already include TLD.
    # If extra is present (and non-empty), append with a dot.
    if extra:
        # ensure we don't double-dot
        if not domain.endswith(".") and not extra.startswith("."):
            return f"{user}@{domain}.{extra}"
        return f"{user}@{domain}{extra}"
    return f"{user}@{domain}"

def parse_meta_html(meta_html: str):
    """
    Parse meta like:
      <a href=javascript:mailto('nanko52','planet.nl','')>PA0V/6X9ELE</a> Nanko xx JO33ii
    Returns dict with email, call, antenna, power, name, state, locator
    """
    soup = BeautifulSoup(meta_html, "html.parser")

    # Anchor may hold call/antenna[/power]; tail text holds name state locator
    a = soup.find("a")
    anchor_text = a.get_text(strip=True) if a else soup.get_text(" ", strip=True)

    # Parse email from href if present
    email = parse_email_from_href(a.get("href")) if a and a.has_attr("href") else None

    # Get the tail text after the <a> (name, state, locator)
    tail_parts = []
    if a:
        for sib in a.next_siblings:
            if isinstance(sib, str):
                tail_parts.append(sib)
            else:
                tail_parts.append(sib.get_text(" ", strip=True))
    else:
        # No anchor: everything after the first token(s) will be in the full text
        pass
    tail_text = " ".join(t.strip() for t in tail_parts if t and t.strip())
    tail_tokens = tail_text.split()

    # Split call/antenna[/power] from anchor text
    call = antenna = power = ""
    cap_parts = [p for p in anchor_text.split("/") if p]
    if len(cap_parts) >= 1:
        call = cap_parts[0].upper()
    if len(cap_parts) >= 2:
        antenna = cap_parts[1]
    if len(cap_parts) >= 3:
        power = cap_parts[2]

    # Extract state and locator from the END of the tail text
    state = locator = ""
    name = ""

    if len(tail_tokens) >= 2 and locator_re.match(tail_tokens[-1]):
        locator = tail_tokens[-1].upper()
        state = tail_tokens[-2].lower()
        name = " ".join(tail_tokens[:-2]).strip()
    else:
        # Best-effort fallback: try to find a locator anywhere and take the token before it as state
        idx = -1
        for i, tok in enumerate(tail_tokens):
            if locator_re.match(tok):
                idx = i
                break
        if idx != -1:
            locator = tail_tokens[idx].upper()
            if idx - 1 >= 0:
                state = tail_tokens[idx - 1].lower()
                name = " ".join(tail_tokens[: idx - 1]).strip()
            else:
                name = " ".join(tail_tokens[:idx]).strip()
        else:
            # If nothing matches expected pattern, treat the whole tail as name
            name = tail_text

    return {
        "email": email or "",
        "call": call,
        "antenna": antenna,
        "power": power,
        "name": name,
        "state": state,
        "locator": locator,
    }


response = requests.get(url)
response.raise_for_status()

for line in response.text.splitlines():
    line = line.strip()
    if not line:
        continue
    m = line_re.match(line)
    if not m:
        continue  # skip lines not matching pattern
    date  = m.group("date")
    utc = m.group("utc")
    message = m.group("message").strip()
    meta_html = m.group("meta").strip()
    meta = parse_meta_html(meta_html)

    print(f"{date} {utc}")
    print(f"  Message : {message}")
    print(f"  Email   : {meta['email']}")
    print(f"  Call    : {meta['call']}")
    print(f"  Antenna : {meta['antenna']}")
    print(f"  Power   : {meta['power']}")
    print(f"  Name    : {meta['name']}")
    print(f"  State   : {meta['state']}")
    print(f"  Locator : {meta['locator']}")
    print("-" * 60)
