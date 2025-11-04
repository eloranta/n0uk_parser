import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.chris.org/cgi-bin/jt65emeA"

# Match whole line
line_re = re.compile(
    r"""
    ^\s*
    (?P<date>\d{2}[A-Za-z]{3})      # e.g., 04Nov
    \s+
    (?P<utc>\d{2}:\d{2})            # e.g., 18:53
    \s+
    (?P<message>.*?)                # message text
    \s*\{\s*
    (?P<meta>.+?)                   # HTML/meta block
    \s*\}\s*$
    """,
    re.VERBOSE,
)

# Extract email from javascript:mailto('user','domain','extra')
mailto_re = re.compile(
    r"^javascript:mailto\('([^']+)','([^']+)','([^']*)'\)\s*$",
    re.IGNORECASE
)

locator_re = re.compile(r"^[A-Za-z]{2}\d{2}[A-Za-z]{2}$")

def fetch_text(url: str) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text.replace("\r\n", "\n").replace("\r", "\n")

def parse_email_from_href(href: str | None) -> str | None:
    if not href:
        return None
    m = mailto_re.match(href.strip())
    if not m:
        return None
    user, domain, extra = m.groups()
    if extra:
        if not domain.endswith(".") and not extra.startswith("."):
            return f"{user}@{domain}.{extra}"
        return f"{user}@{domain}{extra}"
    return f"{user}@{domain}"

def parse_meta_html(meta_html: str):
    soup = BeautifulSoup(meta_html, "html.parser")

    a = soup.find("a")
    anchor_text = a.get_text(strip=True) if a else soup.get_text(" ", strip=True)
    email = parse_email_from_href(a.get("href")) if a and a.has_attr("href") else None

    tail_parts = []
    if a:
        for sib in a.next_siblings:
            if isinstance(sib, str):
                tail_parts.append(sib)
            else:
                tail_parts.append(sib.get_text(" ", strip=True))
    tail_text = " ".join(t.strip() for t in tail_parts if t and t.strip())
    tail_tokens = tail_text.split()

    # Split call/antenna/power
    call = antenna = power = ""
    cap_parts = [p for p in anchor_text.split("/") if p]
    if len(cap_parts) >= 1:
        call = cap_parts[0].upper()
    if len(cap_parts) >= 2:
        antenna = cap_parts[1]
    if len(cap_parts) >= 3:
        power = cap_parts[2]

    # Extract name, state, locator
    name = state = locator = ""
    if len(tail_tokens) >= 2 and locator_re.match(tail_tokens[-1]):
        locator = tail_tokens[-1].upper()
        state = tail_tokens[-2].lower()
        name = " ".join(tail_tokens[:-2]).strip()
    else:
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
            name = tail_text.strip()

    # Replace "xx" with empty string
    if state.lower() == "xx":
        state = ""

    # Truncate locator to first 4 chars if present
    locator = locator[:4] if locator else ""

    return {
        "email": email or "",
        "call": call,
        "antenna": antenna,
        "power": power,
        "name": name,
        "state": state,
        "locator": locator,
    }

def main():
    text = fetch_text(URL)
    any_matches = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = line_re.match(line)
        if not m:
            continue

        date = m.group("date")
        utc = m.group("utc")
        message = m.group("message").strip()
        meta_html = m.group("meta").strip()

        meta = parse_meta_html(meta_html)

        any_matches = True
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

    if not any_matches:
        print("No matching lines found.")

if __name__ == "__main__":
    main()
