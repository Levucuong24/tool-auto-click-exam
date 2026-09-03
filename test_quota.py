import urllib.request, json, ssl, time

key = "YOUR_API_KEY"
models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.6-flash", "gemini-pro-latest"]

headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
payload = {
    "contents": [{"parts": [{"text": "Reply with 'OK'."}]}]
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
    try:
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"{m} => SUCCESS 200: {text}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        print(f"{m} => HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"{m} => ERROR: {e}")
    time.sleep(2)
