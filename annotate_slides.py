from PIL import Image, ImageDraw, ImageFont
import os

images = [
    'slide_1_market_share.png',
    'slide_2_visitor_volume.png',
    'slide_3_avg_spending.png',
    'slide_4_total_revenue.png',
    'slide_5_kpi_dashboard.png',
    'slide_6_growth_scenarios.png',
]

note = 'Data covers CHINESE visitors only (RESAS / MLIT, 2024). See notes for methodology.'

out_dir = 'annotated_slides'
os.makedirs(out_dir, exist_ok=True)

# Try to use a common font; fall back to default
try:
    font = ImageFont.truetype('DejaVuSans.ttf', 14)
except Exception:
    font = ImageFont.load_default()

for img_name in images:
    if not os.path.exists(img_name):
        print(f"Missing: {img_name} - skipping")
        continue
    im = Image.open(img_name).convert('RGBA')
    w, h = im.size
    overlay = Image.new('RGBA', im.size, (255,255,255,0))
    draw = ImageDraw.Draw(overlay)
    text_w, text_h = draw.textsize(note, font=font)
    padding = 10
    x = (w - text_w) // 2
    y = h - text_h - padding
    # draw semi-transparent rectangle
    rect_h = text_h + 8
    rect_y = y - 4
    draw.rectangle([(0, rect_y), (w, rect_y + rect_h)], fill=(255,255,255,200))
    draw.text((x, y), note, fill='black', font=font)
    out = Image.alpha_composite(im, overlay).convert('RGB')
    out_path = os.path.join(out_dir, img_name.replace('.png', '_annotated.png'))
    out.save(out_path, dpi=(300,300))
    print(f'Saved: {out_path}')
