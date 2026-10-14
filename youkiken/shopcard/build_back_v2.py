"""ショップカード裏面の刷新版。スキャン画像を使わず、文字はフォントで組み直す。

- 上: 笑顔ロゴ(トレース版) + 表面の筆文字「陽気軒」
- 中: 電話・営業時間・定休日・住所
- 下: Instagram とホームページのQRを同じ色・同じ形で並べる(中央にアイコン)

案は2つ:
  white … 白地に表面と同じ雷文の枠
  red   … ロゴの臙脂で全面ベタ、文字は白、QRは白いタイルに載せる

要 qrcode[pil]。 使い方: python3 youkiken/shopcard/build_back_v2.py [white|red]
"""
import sys
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

import build_front_raimon as front_kit

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / "print/reference/logo-yohkiken-traced.png"
FRONT = HERE / "front_final_hq.png"

DPI = 800
DPMM = DPI / 25.4
CW, CH = 1732, 2866

RED = (172, 29, 32)       # ロゴの臙脂 #AC1D20
GOLD = (240, 187, 41)     # ロゴの黄金 #F0BB29
INK = (40, 30, 28)
WHITE = (255, 255, 255)

GOTHIC = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

INSTA_URL = "https://www.instagram.com/youkiken_"
HP_URL = "https://youkiken.com/"

# front_final_hq.png 上の筆文字「陽気軒」の範囲
BRUSH_BOX = (560, 2535, 1545, 2835)


def gothic(weight, size):
    return ImageFont.truetype(GOTHIC.format(weight), size)


def mm(v):
    return round(v * DPMM)


def brush_text(color):
    """表面スキャンの筆文字「陽気軒」を墨の濃さをアルファにして指定色で返す。"""
    src = np.asarray(Image.open(FRONT).convert("L").crop(BRUSH_BOX)).astype(float)
    alpha = np.clip((235 - src) / (235 - 60), 0, 1) * 255
    ys, xs = np.where(alpha > 40)
    alpha = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgb = np.empty(alpha.shape + (3,), np.uint8)
    rgb[...] = color
    return Image.fromarray(np.dstack([rgb, alpha.astype(np.uint8)]))


def icon_instagram(size, color, bg):
    s = size * 4
    im = Image.new("RGBA", (s, s), bg + (255,))
    d = ImageDraw.Draw(im)
    w = round(s * 0.09)
    m = round(s * 0.14)
    d.rounded_rectangle((m, m, s - m, s - m), radius=round(s * 0.24), outline=color, width=w)
    r = round(s * 0.18)
    c = s // 2
    d.ellipse((c - r, c - r, c + r, c + r), outline=color, width=w)
    dr = round(s * 0.055)
    dx, dy = round(s * 0.69), round(s * 0.31)
    d.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=color)
    return im.resize((size, size), Image.LANCZOS)


def icon_home(size, color, bg):
    s = size * 4
    im = Image.new("RGBA", (s, s), bg + (255,))
    d = ImageDraw.Draw(im)
    w = round(s * 0.09)
    roof = [(s * 0.14, s * 0.50), (s * 0.50, s * 0.17), (s * 0.86, s * 0.50)]
    d.line(roof, fill=color, width=w, joint="curve")
    d.line([(s * 0.26, s * 0.44), (s * 0.26, s * 0.83), (s * 0.74, s * 0.83), (s * 0.74, s * 0.44)],
           fill=color, width=w, joint="curve")
    d.rectangle((s * 0.43, s * 0.60, s * 0.57, s * 0.83), fill=color)
    return im.resize((size, size), Image.LANCZOS)


def make_qr(url, size, color, icon):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=0, box_size=20)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()).convert("RGB")
    # 黒で描いたものを、明るさをそのままに指定色へ置き換える
    a = np.asarray(img).astype(float) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    img = Image.fromarray((lum * 255 + (1 - lum) * np.array(color)).astype(np.uint8))
    img = img.resize((size, size), Image.LANCZOS)
    ic = round(size * 0.22)
    pad = round(ic * 0.16)
    plate = Image.new("RGB", (ic + 2 * pad, ic + 2 * pad), WHITE)
    plate.paste(icon(ic, color, WHITE), (pad, pad))
    img.paste(plate, ((size - plate.width) // 2, (size - plate.height) // 2))
    return img


def text_center(draw, cx, y, text, font, fill):
    b = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (b[2] - b[0]) / 2 - b[0], y - b[1]), text, font=font, fill=fill)
    return b[3] - b[1]


def pill(draw, cx, y, text, font, fill, text_fill):
    b = draw.textbbox((0, 0), text, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    px, py = round(th * 0.95), round(th * 0.42)
    w, h = tw + 2 * px, th + 2 * py
    draw.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h / 2, fill=fill)
    draw.text((cx - tw / 2 - b[0], y + py - b[1]), text, font=font, fill=text_fill)
    return h


def build(variant):
    on_red = variant == "red"
    bg = RED if on_red else WHITE
    fg = WHITE if on_red else INK
    accent = GOLD if on_red else RED
    accent_text = RED if on_red else WHITE
    sub = (250, 228, 200) if on_red else (95, 80, 76)

    card = Image.new("RGB", (CW, CH), bg)
    draw = ImageDraw.Draw(card)
    cx = CW // 2

    if on_red:
        inset = mm(3.2)
        draw.rectangle((inset, inset, CW - inset, CH - inset), outline=GOLD, width=mm(0.35))
        top, bottom = mm(6.6), CH - mm(5.8)
    else:
        frame, inner = front_kit.build_frame(front_kit.extract_motif(RED))
        card.paste(frame, (0, 0), frame)
        top, bottom = inner + mm(2.5), CH - inner - mm(2.0)

    # ---- 上: ロゴ + 筆文字 ----
    logo_h = mm(8.6)
    logo = Image.open(LOGO).convert("RGB").resize((logo_h, logo_h), Image.LANCZOS)
    brush = brush_text(WHITE if on_red else INK)
    bh = round(logo_h * 0.88)
    brush = brush.resize((round(brush.width * bh / brush.height), bh), Image.LANCZOS)
    gap = mm(2.2)
    lw = logo_h + gap + brush.width
    lx = cx - lw // 2
    if on_red:
        ring = mm(0.6)
        draw.rectangle((lx - ring, top - ring, lx + logo_h + ring, top + logo_h + ring), fill=WHITE)
    card.paste(logo, (lx, top))
    card.paste(brush, (lx + logo_h + gap, top + (logo_h - bh) // 2), brush)
    y = top + logo_h + mm(1.9)
    y += text_center(draw, cx, y, "昭和三十六年創業　ラーメン・中華食堂", ImageFont.truetype(MINCHO, mm(1.75)), sub)

    # ---- 中: 店舗情報 ----
    info_top = y + mm(4.0)
    qr_size = mm(14.0)
    qr_label_h = mm(4.6)
    qr_top = bottom - qr_label_h - qr_size

    blocks = []

    def tel(yy, dry=False):
        d = ImageDraw.Draw(Image.new("RGB", (1, 1))) if dry else draw
        h = text_center(d, cx, yy, "TEL", gothic(6, mm(1.7)), accent if not on_red else GOLD)
        h += mm(0.9)
        h += text_center(d, cx, yy + h, "027-387-7082", gothic(7, mm(4.3)), fg)
        return h

    def hours(yy, dry=False):
        d = ImageDraw.Draw(Image.new("RGB", (1, 1))) if dry else draw
        h = pill(d, cx, yy, "営業時間", gothic(6, mm(1.75)), accent, accent_text)
        h += mm(1.2)
        h += text_center(d, cx, yy + h, "11:00 – 20:00", gothic(7, mm(3.9)), fg)
        h += mm(0.9)
        h += text_center(d, cx, yy + h, "ラストオーダー 19:30", gothic(5, mm(1.75)), sub)
        return h

    def closed(yy, dry=False):
        d = ImageDraw.Draw(Image.new("RGB", (1, 1))) if dry else draw
        h = pill(d, cx, yy, "定休日", gothic(6, mm(1.75)), accent, accent_text)
        h += mm(1.2)
        h += text_center(d, cx, yy + h, "毎月 15日・26日", gothic(7, mm(3.4)), fg)
        h += mm(0.9)
        h += text_center(d, cx, yy + h, "その他、都合によりお休みする場合があります", gothic(4, mm(1.55)), sub)
        return h

    def address(yy, dry=False):
        d = ImageDraw.Draw(Image.new("RGB", (1, 1))) if dry else draw
        h = text_center(d, cx, yy, "〒370-2134", gothic(5, mm(1.7)), sub)
        h += mm(1.0)
        h += text_center(d, cx, yy + h, "群馬県高崎市吉井町塩川37-4", gothic(6, mm(2.25)), fg)
        return h

    blocks = [tel, hours, closed, address]
    heights = [b(0, dry=True) for b in blocks]
    space = qr_top - mm(5.0) - info_top
    step = (space - sum(heights)) / (len(blocks) - 1)
    if step < mm(1.5):
        raise SystemExit(f"情報欄が収まりません (行間 {step / DPMM:.1f}mm)")
    yy = info_top
    for b, h in zip(blocks, heights):
        b(round(yy))
        yy += h + step

    # ---- 下: QR 2つ ----
    qr_color = RED
    col_gap = mm(7.0)
    tile_pad = mm(1.6) if on_red else 0
    lx = cx - col_gap // 2 - qr_size
    rx = cx + col_gap // 2
    for x, url, icon, label in ((lx, INSTA_URL, icon_instagram, "Instagram  @youkiken_"),
                                (rx, HP_URL, icon_home, "ホームページ  youkiken.com")):
        if on_red:
            draw.rounded_rectangle((x - tile_pad, qr_top - tile_pad, x + qr_size + tile_pad, qr_top + qr_size + tile_pad),
                                   radius=mm(1.6), fill=WHITE)
        card.paste(make_qr(url, qr_size, qr_color, icon), (x, qr_top))
        name, handle = label.split("  ")
        ly = qr_top + qr_size + tile_pad + mm(1.3)
        h = text_center(draw, x + qr_size // 2, ly, name, gothic(6, mm(1.7)), accent if not on_red else GOLD)
        text_center(draw, x + qr_size // 2, ly + h + mm(0.7), handle, gothic(5, mm(1.6)), fg)

    out = HERE / f"back_v2_{variant}.png"
    card.save(out, dpi=(DPI, DPI))
    bleed = mm(3)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), bg)
    padded.paste(card, (bleed, bleed))
    padded.save(HERE / f"back_v2_{variant}_bleed3mm.png", dpi=(DPI, DPI))
    print("saved", out.name)


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["white", "red"]):
        build(v)
