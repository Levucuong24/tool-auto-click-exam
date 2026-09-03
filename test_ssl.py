import urllib.request, json, ssl

key = "YOUR_API_KEY"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
headers = {"User-Agent": "Mozilla/5.0"}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        models = [m['name'].replace('models/', '') for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print("MODELS_FOUND:", models)
except Exception as e:
    print("ERROR:", e)
