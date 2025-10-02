# Shopee Affiliate AutoContent Bot

ระบบดึงสินค้า Shopee + สร้างคอนเทนต์อัตโนมัติ พร้อมโพสต์/ส่งต่อไป TikTok/ช่องทางอื่นได้ง่าย

## โครงสร้างโปรเจกต์
ดูรายละเอียดในไฟล์ `docs/deploy.md` และตัวอย่างไฟล์ในแต่ละโฟลเดอร์

## วิธีใช้งาน
1. ตั้งค่าไฟล์ `.env` ตามตัวอย่างใน `.env.example`
2. ติดตั้ง dependencies ด้วย `pip install -r requirements.txt`
3. รัน `python -m src.main` เพื่อสร้างคอนเทนต์

## Automation
- สามารถตั้ง cron หรือใช้ GitHub Actions รันอัตโนมัติ

## หมายเหตุ
- ต้องปรับ endpoint และ signature Shopee API ตามเอกสารจริง
- ดูรายละเอียดเพิ่มเติมในโค้ดแต่ละไฟล์
