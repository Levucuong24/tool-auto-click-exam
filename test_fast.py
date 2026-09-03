import urllib.request, json, ssl

key = "YOUR_API_KEY"
m = "gemini-3.6-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"

headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
payload = {"contents": [{"parts": [{"text": "Reply OK"}]}]}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
        out = f"SUCCESS 200: {res.read().decode('utf-8')[:200]}"
except urllib.error.HTTPError as e:
    out = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
except Exception as e:
    out = f"ERR: {e}"

with open("test_fast_out.txt", "w", encoding="utf-8") as f:
    f.write(out)
