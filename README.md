# Tool Auto Click Exam

Công cụ tự động hóa click và làm bài thi (Auto Click Exam Tool).

## Cài đặt (Installation)

```bash
pip install -r requirements.txt
```

## Cấu hình (Configuration)

Tạo file `config.json` từ `config.json.example` và điền API key của bạn:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "roi": [16, 229, 1727, 132],
  "interval": 300,
  "use_ai": true
}
```

## Sử dụng (Usage)

```bash
python main.py
```
