"""Generate a simple logo texture and apply it to a cube OBJ/MTL pair.

Creates:
 - assets/models/logo_texture.png
 - assets/models/logo_cube.mtl
 - assets/models/logo_cube.obj (copies geometry from uv_cube.obj if present)
 - assets/models/logo_preview.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

MODEL_DIR = os.path.join('assets','models')
os.makedirs(MODEL_DIR, exist_ok=True)

# texture parameters
W = 512
H = 512
bg_color = (255,255,255,255)
circle_color = (30,144,255,255)  # dodgerblue
accent_color = (255,215,0,255)   # gold
text = "Brand"

# create base image
img = Image.new('RGBA', (W,H), bg_color)
d = ImageDraw.Draw(img)

# draw a soft circle with radial blur (approx)
cx, cy = W//2, H//2
r = int(W*0.35)
for i in range(8,0,-1):
    bbox = [cx - r - i*2, cy - r - i*2, cx + r + i*2, cy + r + i*2]
    alpha = int(80 * (i/8))
    d.ellipse(bbox, fill=(circle_color[0], circle_color[1], circle_color[2], alpha))

# center disc
d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=circle_color)

# add accent ring
d.ellipse((cx-r+10, cy-r+10, cx+r-10, cy+r-10), outline=accent_color, width=6)

# add text (fallback to default font)
try:
    font = ImageFont.truetype("arial.ttf", 64)
except Exception:
    font = ImageFont.load_default()

try:
    w, h = d.textsize(text, font=font)
except Exception:
    try:
        bbox = d.textbbox((0,0), text, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
    except Exception:
        w, h = font.getsize(text)

d.text((cx - w//2, cy - h//2), text, fill=(255,255,255,255), font=font)

# subtle shadow
img = img.filter(ImageFilter.GaussianBlur(0.5))

texture_path = os.path.join(MODEL_DIR, 'logo_texture.png')
img.save(texture_path)
print('Wrote', texture_path)

# create MTL that points to our texture
mtl_path = os.path.join(MODEL_DIR, 'logo_cube.mtl')
with open(mtl_path, 'w', encoding='utf-8') as mf:
    mf.write('newmtl material_0\n')
    mf.write('Ka 1.000 1.000 1.000\n')
    mf.write('Kd 1.000 1.000 1.000\n')
    mf.write('Ks 0.000 0.000 0.000\n')
    mf.write('d 1.0\n')
    mf.write('illum 2\n')
    mf.write('map_Kd logo_texture.png\n')
print('Wrote', mtl_path)

# source OBJ to copy geometry from (if exists)
src_obj = os.path.join(MODEL_DIR, 'uv_cube.obj')
dst_obj = os.path.join(MODEL_DIR, 'logo_cube.obj')
if os.path.exists(src_obj):
    with open(src_obj, 'r', encoding='utf-8') as sf:
        data = sf.read()
    # replace mtllib line to point to logo_cube.mtl
    lines = data.splitlines()
    if lines and lines[0].startswith('mtllib'):
        lines[0] = 'mtllib logo_cube.mtl'
    else:
        lines.insert(0, 'mtllib logo_cube.mtl')
    with open(dst_obj, 'w', encoding='utf-8') as df:
        df.write('\n'.join(lines))
    print('Wrote', dst_obj)
else:
    # fallback: generate a simple cube OBJ
    with open(dst_obj, 'w', encoding='utf-8') as df:
        df.write('mtllib logo_cube.mtl\n')
        df.write('v -0.5 -0.5 -0.5\n')
        df.write('v 0.5 -0.5 -0.5\n')
        df.write('v 0.5 0.5 -0.5\n')
        df.write('v -0.5 0.5 -0.5\n')
        df.write('v -0.5 -0.5 0.5\n')
        df.write('v 0.5 -0.5 0.5\n')
        df.write('v 0.5 0.5 0.5\n')
        df.write('v -0.5 0.5 0.5\n')
        df.write('f 1 2 3 4\n')
        df.write('f 5 8 7 6\n')
        df.write('f 1 5 6 2\n')
        df.write('f 2 6 7 3\n')
        df.write('f 3 7 8 4\n')
        df.write('f 5 1 4 8\n')
    print('Wrote (fallback)', dst_obj)

# create a preview PNG (showing logo centered with simple drop shadow)
preview = Image.new('RGBA', (800,600), (240,240,240,255))
pd = ImageDraw.Draw(preview)
# draw a simulated cube face rectangle and paste logo
rect = (250,150,550,450)
pd.rectangle(rect, fill=(200,200,200,255))
# paste texture (scaled) onto the rect center
tex = Image.open(texture_path).convert('RGBA')
tex = tex.resize((260,260), Image.LANCZOS)
preview.paste(tex, (270,170), tex)
# add caption
try:
    font = ImageFont.truetype('arial.ttf', 24)
except Exception:
    font = ImageFont.load_default()
caption = 'Sample 3D Cube with generated logo texture'
try:
    w,h = pd.textsize(caption, font=font)
except Exception:
    try:
        bbox = pd.textbbox((0,0), caption, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
    except Exception:
        w,h = font.getsize(caption)
pd.text(((800-w)//2, 520), caption, fill=(30,30,30,255), font=font)
preview_path = os.path.join(MODEL_DIR, 'logo_preview.png')
preview.save(preview_path)
print('Wrote', preview_path)
