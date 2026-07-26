import urllib.request
import json
import ssl
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.github.com/repos/mantbyte/mantbyte.github.io/actions/runs"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, context=ctx) as response:
    data = json.loads(response.read().decode())
    for run in data.get("workflow_runs", []):
        if run["name"] == "Daily Digest Distribution":
            print(f"Run ID: {run['id']}, Status: {run['status']}, Conclusion: {run['conclusion']}")
            jobs_url = run["jobs_url"]
            req2 = urllib.request.Request(jobs_url)
            with urllib.request.urlopen(req2, context=ctx) as r2:
                jobs_data = json.loads(r2.read().decode())
                for job in jobs_data.get("jobs", []):
                    print(f"  Job {job['name']}: {job['status']} - {job['conclusion']}")
            break
