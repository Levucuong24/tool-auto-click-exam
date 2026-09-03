import urllib.request, json, sys

key = "YOUR_API_KEY"

for ver in ["v1beta", "v1"]:
    url = f"https://generativelanguage.googleapis.com/{ver}/models?key={key}"
    print(f"Testing {ver}...", flush=True)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            names = [m['name'] for m in data.get('models', [])]
            print(f"VER {ver} OK! Found {len(names)} models:", names, flush=True)
    except Exception as e:
        print(f"VER {ver} ERR:", e, flush=True)
