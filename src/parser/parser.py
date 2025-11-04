import requests
from bs4 import BeautifulSoup
import re

# URL to fetch
url = "https://www.chris.org/cgi-bin/jt65emeA"

# Send a GET request
response = requests.get(url)
response.raise_for_status()  # Raise an error if the request failed

# Parse HTML content with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Extract all text and split into lines
text = re.sub(r'[\r\n\t]+', '\n', response.text)  # normalize line endings
text = re.sub(r'[^\x20-\x7E\n]+', '', text)       # remove non-printable ASCII
lines = [line.strip() for line in text.splitlines() if line.strip()]

# Print each line one by one
for line in lines:
    print(line)
