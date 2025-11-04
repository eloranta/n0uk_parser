import requests

url = "https://www.chris.org/cgi-bin/jt65emeA"
response = requests.get(url)
response.raise_for_status()

for line in response.text.splitlines():
    line = line.strip()
    if line:
        print(line)
