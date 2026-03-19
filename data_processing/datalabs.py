# Code from www.datalab.to to process the pdf to markdown using their API

import requests, time,dotenv, json, explanations

key=dotenv.get_key(".env", "DATALABS_API_KEY")


url = "https://www.datalab.to/api/v1/convert"
headers = {"X-Api-Key": key}

file = explanations.get_file_from_user()

with open(file, "rb") as f:
    resp = requests.post(
        url,
        files={"file": (file, f, "application/pdf")},
        headers=headers,
    )

print (json.dumps(resp.json(), indent=4))

check_url = resp.json()["request_check_url"]

# Poll until complete
for _ in range(300):
    r = requests.get(check_url, headers=headers).json()
    if r["status"] == "complete":
        break
    time.sleep(2)
with open("assets/mathematics-example.md", "w") as f:
    f.write(r["markdown"])
with open("assets/mathematics-full.json", "r") as f:
    f.write(r)