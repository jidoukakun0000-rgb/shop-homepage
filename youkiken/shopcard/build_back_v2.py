"""ショップカード裏面の刷新版。スキャン画像を使わず、文字はフォントで組み直す。

- 上: 笑顔ロゴ(トレース版) + 表面の筆文字「陽気軒」
- 中: 電話・営業時間・定休日・住所
- 下: Instagram とホームページのQRを同じ色・同じ形で並べる(中央にアイコン)

白地・枠なし。住所とQRの間に「まんぷく定食」のキャラ(manpuku-boy.png)を寝かせる。

要 qrcode[pil]。 使い方: python3 youkiken/shopcard/build_back_v2.py [chara|plain]
"""
import sys
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / "print/reference/logo-yohkiken-traced.png"
CHARA = HERE.parent / "print/reference/manpuku-boy.png"
FRONT = HERE / "front_final_hq.png"

DPI = 800
DPMM = DPI / 25.4
CW, CH = 1732, 2866

RED = (172, 29, 32)       # ロゴの臙脂 #AC1D20
INK = (40, 30, 28)
QR_COLOR = INK            # QRは本文と同じ墨色
WHITE = (255, 255, 255)

GOTHIC = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

INSTA_URL = "https://www.instagram.com/youkiken_"
HP_URL = "https://youkiken.com/"

# ---- お店に確認中の文言 ----
# None にすると描かない。「◯」を含む部分は青字で描き、残っていれば警告を出す
SUBTITLE = "昭和三十六年創業　名物ジャンボ餃子と自家製麺"
ACCESS = None     # 例: "上信電鉄 吉井駅 徒歩10分"
PARKING = None    # 例: "駐車場 ◯台"
BUBBLE = None     # 例: ("汁物以外は", "お持ち帰り", "できるよ！")  ※お持ち帰りは汁物以外OK(お店に確認済み)
TBD = "◯"
TBD_COLOR = (0, 120, 255)

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


IG_STOPS = [(0.0, (0xfd, 0xf4, 0x97)), (0.05, (0xfd, 0xf4, 0x97)), (0.45, (0xfd, 0x59, 0x49)),
            (0.6, (0xd6, 0x24, 0x9f)), (0.9, (0x28, 0x5a, 0xeb))]


def icon_instagram_color(size, color=None, bg=None):
    """メニュー表と同じ、Instagram公式のグラデーションのアプリアイコン(背景透過)。"""
    s = size * 4
    yy, xx = np.mgrid[0:s, 0:s] / s
    t = np.clip(np.hypot(xx - 0.3, yy - 1.07) / 1.5, 0, 1)
    pos = [p for p, _ in IG_STOPS]
    rgb = np.stack([np.interp(t, pos, [c[i] for _, c in IG_STOPS]) for i in range(3)], axis=-1)
    im = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=round(s * 6.5 / 24), fill=255)
    im.putalpha(mask)
    d = ImageDraw.Draw(im)
    w = round(s * 2 / 24)
    d.rounded_rectangle((s * 5 / 24, s * 5 / 24, s * 19 / 24, s * 19 / 24), radius=round(s * 4 / 24), outline="white", width=w)
    r = s * 3.3 / 24
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline="white", width=w)
    r = s * 1.05 / 24
    d.ellipse((s * 16.3 / 24 - r, s * 7.7 / 24 - r, s * 16.3 / 24 + r, s * 7.7 / 24 + r), fill="white")
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
    # 中央の白い台はQRのマス目に揃えて、切れたドットが細い線で残らないようにする
    n = qr.modules_count
    k = max(3, round(n * 0.30))
    if (n - k) % 2:
        k += 1
    m0 = (n - k) // 2
    ImageDraw.Draw(img).rectangle((m0 * 20, m0 * 20, (m0 + k) * 20 - 1, (m0 + k) * 20 - 1), fill=WHITE)
    img = img.resize((size, size), Image.LANCZOS)
    plate = round(size * k / n)
    ic = round(plate * 0.74)
    ico = icon(ic, color, WHITE)
    img.paste(ico, ((size - ic) // 2, (size - ic) // 2), ico)
    return img


def text_center(draw, cx, y, text, font, fill):
    b = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (b[2] - b[0]) / 2 - b[0], y - b[1]), text, font=font, fill=fill)
    return b[3] - b[1]


def text_center_parts(draw, cx, y, parts, font):
    """色の違う文字列を1行に並べて中央揃えで描く。parts は [(文字列, 色), ...]"""
    widths = [draw.textlength(t, font=font) for t, _ in parts]
    b = draw.textbbox((0, 0), "".join(t for t, _ in parts), font=font)
    x = cx - sum(widths) / 2
    for (t, c), w in zip(parts, widths):
        draw.text((x, y - b[1]), t, font=font, fill=c)
        x += w
    return b[3] - b[1]


def tbd_color(text, normal):
    return TBD_COLOR if TBD in text else normal


def speech_bubble(draw, x, y, lines, font, tip, color, fill):
    """左側に尻尾の付いた吹き出しを (x, y) を左上にして描き、幅と高さを返す。"""
    lh = [draw.textbbox((0, 0), t, font=font) for t in lines]
    tw = max(b[2] - b[0] for b in lh)
    line_h = max(b[3] - b[1] for b in lh)
    lead = round(line_h * 0.45)
    pad_x, pad_y = mm(1.1), mm(0.9)
    w = tw + 2 * pad_x
    h = line_h * len(lines) + lead * (len(lines) - 1) + 2 * pad_y
    ow = max(2, mm(0.22))
    draw.rounded_rectangle((x, y, x + w, y + h), radius=mm(1.4), fill=fill, outline=color, width=ow)
    y1, y2 = y + h * 0.48, y + h * 0.72
    draw.polygon([(x + ow, y1), tip, (x + ow, y2)], fill=fill, outline=color)
    draw.line([(x + ow / 2, y1 + ow), (x + ow / 2, y2 - ow)], fill=fill, width=ow + 2)
    for i, (t, b) in enumerate(zip(lines, lh)):
        ty = y + pad_y + i * (line_h + lead)
        draw.text((x + w / 2 - (b[2] - b[0]) / 2 - b[0], ty - b[1]), t, font=font, fill=INK)
    return w, h


def pill(draw, cx, y, text, font, fill, text_fill):
    b = draw.textbbox((0, 0), text, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    px, py = round(th * 0.95), round(th * 0.42)
    w, h = tw + 2 * px, th + 2 * py
    draw.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h / 2, fill=fill)
    draw.text((cx - tw / 2 - b[0], y + py - b[1]), text, font=font, fill=text_fill)
    return h


def build(variant):
    with_chara = variant == "chara"
    fg, sub = INK, (95, 80, 76)

    card = Image.new("RGB", (CW, CH), WHITE)
    draw = ImageDraw.Draw(card)
    cx = CW // 2
    top, bottom = mm(5.5), CH - mm(4.5)

    # ---- 上: ロゴ + 筆文字 ----
    logo_h = mm(8.6)
    logo = Image.open(LOGO).convert("RGB").resize((logo_h, logo_h), Image.LANCZOS)
    brush = brush_text(INK)
    bh = round(logo_h * 0.88)
    brush = brush.resize((round(brush.width * bh / brush.height), bh), Image.LANCZOS)
    gap = mm(2.2)
    lx = cx - (logo_h + gap + brush.width) // 2
    card.paste(logo, (lx, top))
    card.paste(brush, (lx + logo_h + gap, top + (logo_h - bh) // 2), brush)
    y = top + logo_h + mm(1.9)
    # 名刺で読める 6pt 以上にすると1行に入らないので、創業と名物で2行に分ける
    for i, line in enumerate(SUBTITLE.split("　")):
        y += (mm(0.7) if i else 0)
        y += text_center(draw, cx, y, line, ImageFont.truetype(MINCHO, mm(2.15)), tbd_color(line, sub))

    # ---- 下から: QR 2つ、その上にキャラ ----
    qr_size = mm(14.0)
    qr_top = bottom - mm(3.2) - qr_size
    chara_h = mm(12.0) if with_chara else 0
    chara_top = qr_top - mm(1.2) - chara_h

    # ---- 中: 店舗情報 ----
    info_top = y + mm(4.0)

    def tel(d, yy):
        h = text_center(d, cx, yy, "TEL", gothic(6, mm(2.1)), RED)
        h += mm(0.9)
        h += text_center(d, cx, yy + h, "027-387-7082", gothic(7, mm(4.3)), fg)
        return h

    col_off = mm(10.5)

    def hours_closed(d, yy):
        hl = pill(d, cx - col_off, yy, "営業時間", gothic(6, mm(2.2)), RED, WHITE)
        pill(d, cx + col_off, yy, "定休日", gothic(6, mm(2.2)), RED, WHITE)
        h = hl + mm(1.2)
        # 閉店時刻は日によって違うので書かない(店主の案: 11時から品切れまで)
        a = text_center(d, cx - col_off, yy + h, "11:00〜", gothic(7, mm(2.9)), fg)
        text_center(d, cx + col_off, yy + h, "毎月15日・26日", gothic(7, mm(2.9)), fg)
        h += a + mm(0.9)
        return h + text_center(d, cx - col_off, yy + h, "品切れ次第終了", gothic(6, mm(2.15)), sub)

    def address(d, yy):
        h = text_center(d, cx, yy, "〒370-2134", gothic(5, mm(2.15)), sub)
        h += mm(1.0)
        h += text_center(d, cx, yy + h, "群馬県高崎市吉井町塩川37-4", gothic(6, mm(2.6)), fg)
        extra = [t for t in (ACCESS, PARKING) if t]
        if extra:
            parts = []
            for t in extra:
                parts += [(t, tbd_color(t, sub)), ("　", sub)]
            h += mm(1.0)
            h += text_center_parts(d, cx, yy + h, parts[:-1], gothic(5, mm(2.1)))
        return h

    blocks = [tel, hours_closed, address]
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    heights = [b(scratch, 0) for b in blocks]
    info_bottom = (chara_top if with_chara else qr_top) - mm(3.0 if with_chara else 5.0)
    step = (info_bottom - info_top - sum(heights)) / (len(blocks) - 1)
    if step < mm(1.5):
        raise SystemExit(f"情報欄が収まりません (行間 {step / DPMM:.1f}mm)")
    yy = info_top
    for b, h in zip(blocks, heights):
        b(draw, round(yy))
        yy += h + step

    if with_chara:
        boy = Image.open(CHARA).convert("RGBA")
        boy = boy.resize((round(boy.width * chara_h / boy.height), chara_h), Image.LANCZOS)
        bx = cx - (mm(5.0) if BUBBLE else 0) - boy.width // 2
        card.paste(boy, (bx, chara_top), boy)
        if BUBBLE:
            # 吹き出しは頭の右に置き、尻尾を口元へ向ける
            tip = (bx + boy.width * 0.80, chara_top + chara_h * 0.36)
            bub_x = bx + round(boy.width * 0.90) + mm(1.2)
            bw, _ = speech_bubble(draw, bub_x, chara_top - mm(0.6), BUBBLE, gothic(6, mm(2.1)), tip, RED, WHITE)
            if bub_x + bw > CW - mm(3.5):
                raise SystemExit("吹き出しがカードの端にかかります")

    col_gap = mm(7.0)
    lx = cx - col_gap // 2 - qr_size
    rx = cx + col_gap // 2
    f = gothic(6, mm(2.1))
    for x, url, icon, label in ((lx, INSTA_URL, icon_instagram_color, "@youkiken_"),
                                (rx, HP_URL, icon_home, "youkiken.com")):
        card.paste(make_qr(url, qr_size, QR_COLOR, icon), (x, qr_top))
        ly = qr_top + qr_size + mm(1.3)
        qcx = x + qr_size // 2
        if icon is icon_instagram_color:
            b = draw.textbbox((0, 0), label, font=f)
            tw, th = b[2] - b[0], b[3] - b[1]
            isz, igap = round(th * 1.3), mm(0.7)
            x0 = qcx - (isz + igap + tw) // 2
            ig = icon_instagram_color(isz)
            card.paste(ig, (x0, ly + (th - isz) // 2), ig)
            draw.text((x0 + isz + igap - b[0], ly - b[1]), label, font=f, fill=fg)
        else:
            text_center(draw, qcx, ly, label, f, fg)

    out = HERE / f"back_v2_{variant}.png"
    card.save(out, dpi=(DPI, DPI))
    bleed = mm(3)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), WHITE)
    padded.paste(card, (bleed, bleed))
    padded.save(HERE / f"back_v2_{variant}_bleed3mm.png", dpi=(DPI, DPI))
    print("saved", out.name, f"(行間 {step / DPMM:.1f}mm)")
    pending = [t for t in (SUBTITLE, ACCESS, PARKING, *(BUBBLE or ())) if t and TBD in t]
    if pending:
        print("※ 仮置きが残っています(青字):", " / ".join(pending))


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["chara"]):
        build(v)
