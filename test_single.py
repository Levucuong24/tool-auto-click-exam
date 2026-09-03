import urllib.request, json

key = "YOUR_API_KEY"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": "Hi"}]}]}

try:
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=5) as res:
        out = f"STATUS: {res.status}\nBODY: {res.read().decode('utf-8')[:300]}"
except urllib.error.HTTPError as e:
    out = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
except Exception as e:
    out = f"EXC: {e}"

with open("out.txt", "w", encoding="utf-8") as f:
    f.write(out)
