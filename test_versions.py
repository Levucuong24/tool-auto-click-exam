import urllib.request, json

key = "YOUR_API_KEY"

for ver in ["v1", "v1beta", "v1alpha"]:
    url = f"https://generativelanguage.googleapis.com/{ver}/models?key={key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            model_names = [m['name'] for m in data.get('models', [])]
            print(f"API {ver} SUCCESS! Models ({len(model_names)}): {model_names[:10]}")
    except urllib.error.HTTPError as e:
        print(f"API {ver} HTTP {e.code}: {e.read().decode('utf-8')[:150]}")
    except Exception as e:
        print(f"API {ver} EXC: {e}")
