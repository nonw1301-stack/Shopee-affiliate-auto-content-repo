# How to rotate TikTok client secret locally and re-authorize

1. In TikTok Developer Console: Reset (rotate) the client secret for your app and copy the new value.

2. Run the PowerShell helper (from repo root):

   .\scripts\rotate_tiktok_secret.ps1 -ClientKey AWD551S8FF0G2R8N -NewSecret '<NEW_SECRET>'

   This updates `.env` in the repo root and removes the local encrypted token store (`.tokens.enc`).

3. Re-run the connect flow to re-authorize and persist tokens:

   .\scripts\connect_tiktok.ps1

4. Verify tokens:

   python -m scripts.check_tokens

## วิธี Verify ที่หน้า TikTok Developer Console (ทีละภาพ/ทีละขั้นตอน) — ภาษาไทย

ต่อไปนี้เป็นขั้นตอนที่แนะนำให้ทำตอนที่ TikTok ขอให้คุณยืนยันเว็บไซต์ (Site Verification) โดยเราจะใช้ไฟล์ที่อัปโหลดใน `docs/` บน GitHub Pages

1) เปิดหน้า TikTok Developer Console แล้วไปที่แอปของคุณ
   - ตัวอย่าง: Developer Console → My Apps → เลือกแอปที่ต้องการ

2) หาเมนู ‘Site Verification’ หรือปุ่ม ‘Verify’ (ตำแหน่งจะแตกต่างกันตาม UI ของ TikTok)

3) ในช่องให้ใส่ URL ให้วางหนึ่งใน URL ต่อไปนี้ (เริ่มจากไฟล์ exact .txt หาก TikTok ให้ไฟล์ key=value):
   - Exact key=value file: `https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok6BhCfHOzgJpfpHRdyUu0KRLFBWqYHWzh.txt`
   - Non-trailing HTML: `https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok-verify-awd551s8ff0g2r8n.html`
   - Trailing-slash folder fallback: `https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok-verify-awd551s8ff0g2r8n/`
   - Plain text token: `https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok-verify-awd551s8ff0g2r8n.txt`
   - Redundant HTML variant: `https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok-verify-redundant-awd551s8ff0g2r8n.html`

4) กดปุ่ม Verify

5) ถ้าขึ้นข้อความว่า "Your property could not be verified" ให้ทำตามนี้ทีละข้อ (สำคัญ — อย่าลบหรือเปลี่ยนค่าใน Console):
   - ดูข้อความหรือ popup ที่ขึ้นมาว่า TikTok พยายามเข้าถึง URL ไหน (บางครั้งจะแสดง URL ที่เขาเรียก เช่น เพิ่ม trailing slash หรือใส่ ".html/" ต่อท้าย)
   - ถ้าเห็น URL ใน popup/ข้อความ ให้ copy URL นั้นมาแล้วส่งมาให้ผม (หรือถ่าย screenshot ของ popup) — ผมจะไปเรียก URL เดียวกันแบบ exact และเปรียบเทียบผลที่ได้

6) วิธี capture ข้อความ/URL / screenshot ที่ง่าย:
   - Windows: กด Win+Shift+S เพื่อใช้ Snip & Sketch แล้วเลือกหน้าต่าง popup ของ TikTok Console แล้วบันทึก
   - หรือคลิกที่ popup แล้วดู console log ของ browser (F12) → Network → ดู request ที่มีสถานะ 404 หรือ request ไปยัง path ที่เกี่ยวกับ `tiktok-verify` และส่งค่อน

7) ถ้าคุณส่ง screenshot หรือ URL ที่ TikTok เรียกจริงมาแล้ว ผมจะ:
   - Fetch URL เดียวกัน (รวม trailing slash/extension) และคืนค่า HTTP status, headers และ body แบบ raw ให้คุณดู
   - ถ้าเนื้อหาไม่ตรง ผมจะเพิ่มไฟล์/variant ใหม่ (เช่น เพิ่มไฟล์ชื่อพิเศษ, สร้าง .html index ใน folder เพิ่มเติม, หรือเปลี่ยน content-type เป็น text/plain) และ push ให้ใหม่

8) หลังการแก้ไขไฟล์ ผมจะแจ้งให้คุณลอง Verify ใหม่ทันที

หมายเหตุเพิ่มเติม:
   - GitHub Pages อาจมี caching เล็กน้อย ถ้าเพิ่ง push ให้รอ 1–2 นาทีแล้วลอง Verify ใหม่
   - อย่าเปลี่ยนชื่อไฟล์หรือแก้ไขเนื้อหาใน `docs/` ด้วยตัวเองระหว่างการทดสอบ ถ้าต้องการแก้ให้แจ้งผมก่อน

ถ้าต้องการ ผมช่วยเขียนคำสั่ง PowerShell แบบสั้นให้คุณดึง HTML body ของ URL ที่ TikTok พยายามเข้าถึง (เพื่อยืนยันเนื้อหา) — บอกผมว่าต้องการหรือเปล่า

### วิธีตรวจด้วยสคริปต์ PowerShell (local)

ผมเพิ่มสคริปต์ helper `scripts/fetch_url.ps1` เพื่อช่วยดึง status, headers และส่วนต้นของ body ของ URL ที่ TikTok เรียก (ใช้สำหรับ debug)

ตัวอย่างการรัน (จากโฟลเดอร์ repo root ใน PowerShell):

```powershell
.\scripts\fetch_url.ps1 -Url "https://nonw1301-stack.github.io/Shopee-affiliate-auto-content-repo/tiktok-verify-awd551s8ff0g2r8n.html"
```

สคริปต์จะแสดง HTTP status, headers และตัวอย่าง body (2000 ตัวอักษรเริ่มต้น) — ถ้าต้องการบันทึกผลเต็ม ๆ ให้ pipe ไปยัง `Out-File` เช่น:

```powershell
.\scripts\fetch_url.ps1 -Url "<URL>" | Out-File full_response.txt
```

