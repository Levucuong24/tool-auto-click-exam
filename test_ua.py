import urllib.request, json

key = "YOUR_API_KEY"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        models = [m['name'].replace('models/', '') for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print("MODELS_LIST:", models)
except Exception as e:
    print("ERROR:", e)
