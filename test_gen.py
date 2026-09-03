import urllib.request
import urllib.error
import json

key = "YOUR_API_KEY"
models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-1.5-pro-latest", "gemini-2.0-flash-exp", "gemini-pro-vision"]

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}]
}

headers = {"Content-Type": "application/json"}

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"{m} -> OK {res.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        print(f"{m} -> HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"{m} -> ERROR {e}")
