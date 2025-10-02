# Shopee Affiliate AutoContent Bot

ระบบดึงสินค้า Shopee + สร้างคอนเทนต์ (Caption + Banner) อัตโนมัติ พร้อมเตรียมไฟล์เพื่อโพสต์บน TikTok / Facebook / Instagram

## สถานะปัจจุบัน
- ดึงสินค้า (ตัวอย่างโค้ดใน `src/shopee_client.py` — ต้องแทน endpoint/signature ตาม Shopee Partner API)
- สร้าง Caption โดยใช้ OpenAI (wrapper ใน `src/openai_client.py`)
- สร้างไฟล์ text (caption + affiliate link) และ Banner (ตัวอย่าง `src/media_creator.py`)
- เก็บสถานะรายการที่โพสต์แล้วใน SQLite (`src/db.py`) เพื่อป้องกันการโพสต์ซ้ำ
- Retry/backoff และ logging เบื้องต้น สำหรับ Shopee client
- Unit test เบื้องต้นสำหรับ `src/generator.py`

## โครงสร้างโปรเจกต์
```
shopee-affiliate-auto-content-repo/
├─ README.md
├─ .env.example
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .github/workflows/cron_publish.yml
├─ src/
│  ├─ config.py
│  ├─ shopee_client.py
│  ├─ openai_client.py
│  ├─ generator.py
│  ├─ media_creator.py
│  ├─ poster.py
│  └─ main.py
├─ scripts/
│  └─ openai_example.py
└─ tests/
	└─ test_generator.py
```

## การติดตั้ง (local)
1. สร้าง virtualenv (แนะนำ):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. ติดตั้ง dependencies:

```powershell
pip install -r requirements.txt
```

3. คัดลอก `.env.example` เป็น `.env` และเติมค่า:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
SHOPEE_PARTNER_ID=...
SHOPEE_PARTNER_KEY=...
SHOPEE_API_BASE=https://partner.shopeemobile.com/api/v1
OUTPUT_DIR=./output
MAX_PRODUCTS=5
```

> หมายเหตุ: อย่า commit `.env` หรือค่า secret ลงใน repo (ไฟล์ `.env` ถูกเพิ่มใน `.gitignore`).

4. ทดสอบ OpenAI (ตัวอย่าง):

```powershell
python scripts/openai_example.py
```

5. รันโปรแกรมหลัก เพื่อสร้างคอนเทนต์:

```powershell
python -m src.main
```

ไฟล์ผลลัพธ์จะอยู่ในโฟลเดอร์ `output/` และสถานะถูกเก็บใน `data.db` (SQLite).

## GitHub Actions (CI / cron)
มี workflow ตัวอย่าง `.github/workflows/cron_publish.yml` ที่รัน `python -m src.main` ตามตารางเวลา

ก่อนใช้งานใน GitHub ให้เพิ่ม repository Secrets (Settings → Secrets and variables → Actions):

- `OPENAI_API_KEY` — คีย์ OpenAI
- `SHOPEE_PARTNER_ID` — Shopee partner id
- `SHOPEE_PARTNER_KEY` — Shopee partner key

ตัวอย่าง workflow จะอ่าน Secrets เหล่านี้เป็น environment variables ขณะรัน

## Docker
รันด้วย Docker (ตัวอย่าง):

```powershell
docker build -t shopee-bot .
docker run --env-file .env -v ${PWD}/output:/app/output shopee-bot
```

หรือใช้ docker-compose:

```powershell
docker-compose up --build
```

## Testing
รัน unit tests ด้วย pytest:

```powershell
$env:PYTHONPATH = "."
pytest -q
```

## To-Do / Next steps
- เชื่อมต่อ Shopee API จริง (signature, endpoints)
- เพิ่มการโพสต์ไปยัง TikTok/Instagram (API หรือ automation)
- เพิ่ม logging/monitoring และ retry policies ที่ละเอียดขึ้น
- เพิ่ม unit/integration tests เพิ่มเติม

หากต้องการ ผมจะช่วย:
- A: Implement Shopee signature & real endpoints
- B: Integrate social posting (เลือกวิธีการ)
- C: Harden retry/observability and add CI test matrix

บอกผมได้เลยว่าต้องการให้เริ่มงานข้อไหนต่อ — ผมจะดำเนินการและอัปเดตทีละขั้นตอน

### ตัวอย่าง `.env` เพิ่มเติม (TikTok)

เพิ่มค่าเหล่านี้ใน `.env` หรือ environment ของคุณ:

```
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=http://localhost:8080/tiktok/callback
```

### สร้าง Authorization URL แบบ CLI

ใช้สคริปต์ช่วยสร้าง URL:

```powershell
python scripts/make_authorize_url.py --client-key your_client_key --redirect-uri http://localhost:8080/tiktok/callback
```


## OAuth (TikTok) — การตั้งค่าและตัวอย่าง

ขั้นตอนเบื้องต้น:

1. กำหนด environment variables ใน `.env` หรือระบบของคุณ:

```
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=http://localhost:8080/tiktok/callback
```

2. รัน service callback (docker-compose จะมี service `oauth` รันที่พอร์ต 8080):

```powershell
docker-compose up --build
```

3. สร้าง URL สำหรับให้ผู้ใช้กดอนุญาต (authorization URL):

ใน Python shell หรือ script:

```python
from src.poster_tiktok_api import get_authorize_url
url = get_authorize_url(client_key="your_client_key", redirect_uri="http://localhost:8080/tiktok/callback")
print(url)
```

4. เปิด URL ที่ได้ในเบราว์เซอร์ — หลังจากอนุญาต แอปจะ redirect กลับมาที่ `TIKTOK_REDIRECT_URI` ซึ่งจะถูก FastAPI endpoint `/tiktok/callback` รับและแลก `code` → `token` ให้โดยอัตโนมัติ

5. เมื่อ token ถูกแลกและบันทึกไว้แล้ว (via `token_store`), runner สามารถเรียกใช้งาน `--run` เพื่อใช้ token ที่บันทึกไว้ในการอัพโหลดจริง

หมายเหตุความปลอดภัย: เก็บ `TIKTOK_CLIENT_SECRET` และ token ใน secret manager ที่ปลอดภัย; ห้าม commit ลงใน repo

