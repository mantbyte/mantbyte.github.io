import os
from google import genai

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("NO API KEY")
else:
    client = genai.Client(api_key=key)
    for m in client.models.list():
        print(m.name)
