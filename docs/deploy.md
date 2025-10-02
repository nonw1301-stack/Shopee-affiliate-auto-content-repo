# Deployment

## วิธีใช้งาน
1. ตั้งค่าไฟล์ `.env` ตามตัวอย่างใน `.env.example`
2. ติดตั้ง dependencies ด้วย `pip install -r requirements.txt`
3. รัน `python -m src.main` เพื่อสร้างคอนเทนต์

## Automation
- สามารถตั้ง cron หรือใช้ GitHub Actions รันอัตโนมัติ
- ตัวอย่าง workflow ดูที่ `.github/workflows/cron_publish.yml`
