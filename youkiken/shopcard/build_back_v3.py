"""ショップカード裏面(元の裏面の雰囲気を活かした版)。

元の裏面(back_final_hq.png)の構成はそのまま:
  茶色の「陽気軒」看板 / 電話アイコン+番号 / 茶色の丸い見出し「営業時間」「定休日」 / 住所 / QR
看板と電話アイコンはスキャンから切り出して茶・白の2色に整え、文字は丸ゴシックで打ち直す。
並べ方は「関連する情報は詰めて、まとまりどうしの間隔は同じ」にそろえる。
お持ち帰りは汁物以外OK(2026-10 お店に確認済み)。
QRは Instagram と ホームページ(youkiken.com)の2つ。

要 qrcode[pil]。 使い方: python3 youkiken/shopcard/build_back_v3.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import build_back_v2 as kit
from build_back_v2 import CW, CH, DPI, WHITE, mm

HERE = Path(__file__).resolve().parent
SRC = HERE / "back_final_hq.png"
OUT = HERE / "back_v3.png"
OUT_BLEED = HERE / "back_v3_bleed3mm.png"

BROWN = (92, 63, 61)            # 元の裏面の茶色(実測)
NOTE = (128, 104, 100)
ROUND = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"

SIGN_BOX = (477, 123, 1262, 412)      # back_final_hq.png 上の看板
TEL_ICON_BOX = (172, 563, 408, 751)   # 同じく電話アイコン

MARGIN_X = 5.0
TOP, BOTTOM = 4.8, 4.5          # 上下の余白(mm)


# 文字は名刺で読める大きさとして 6pt(約2.1mm)以上にする
def rfont(size_mm):
    return ImageFont.truetype(ROUND, mm(size_mm))


def bold_text(draw, xy, text, f, fill, weight):
    """丸ゴシックは W4 しかないので、同じ色の縁取りで太らせる。"""
    draw.text(xy, text, font=f, fill=fill, stroke_width=weight, stroke_fill=fill)


def measure(draw, text, f, weight=0):
    b = draw.textbbox((0, 0), text, font=f, stroke_width=weight)
    return b, b[2] - b[0], b[3] - b[1]


def two_tone(img, dark, light, lo, hi):
    """明るさで dark〜light の2色に塗り分ける(境目はなめらかに)。"""
    lum = np.asarray(img.convert("L")).astype(float)
    t = np.clip((lum - lo) / (hi - lo), 0, 1)[..., None]
    out = np.array(dark) * (1 - t) + np.array(light) * t
    return Image.fromarray(out.astype(np.uint8))


def sign(width):
    src = Image.open(SRC).convert("RGB").crop(SIGN_BOX)
    im = two_tone(src, BROWN, WHITE, 110, 190)
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def tel_icon(height):
    """スキャンの電話アイコンを、ぼかしてから閾値を取って線をなめらかにする(背景透過)。"""
    src = Image.open(SRC).convert("L").crop(TEL_ICON_BOX)
    big = src.resize((src.width * 4, src.height * 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
    lum = np.asarray(big).astype(float)
    alpha = np.clip((175 - lum) / 40, 0, 1) * 255
    rgb = np.empty(alpha.shape + (3,), np.uint8)
    rgb[...] = BROWN
    im = Image.fromarray(np.dstack([rgb, alpha.astype(np.uint8)]))
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def main():
    card = Image.new("RGB", (CW, CH), WHITE)
    d = ImageDraw.Draw(card)
    cx = CW // 2
    W_BIG = mm(0.11)   # 太字の縁取り幅

    # ---- まとまりを「描く関数」として用意し、高さを先に測る ----
    sg = sign(mm(25.0))

    def g_sign(y, draw=True):
        if draw:
            card.paste(sg, (cx - sg.width // 2, y))
        return sg.height

    num_f = rfont(4.4)
    ic = tel_icon(mm(4.2))

    def g_tel(y, draw=True):
        b, tw, th = measure(d, "027-387-7082", num_f, W_BIG)
        gap = mm(1.6)
        total = ic.width + gap + tw
        x0 = cx - total // 2
        h = max(th, ic.height)
        if draw:
            card.paste(ic, (x0, y + (h - ic.height) // 2), ic)
            bold_text(d, (x0 + ic.width + gap - b[0], y + (h - th) // 2 - b[1]), "027-387-7082", num_f, BROWN, W_BIG)
        return h

    pill_f = rfont(2.2)

    def pill(y, text, draw=True):
        b, tw, th = measure(d, text, pill_f, mm(0.035))
        px, py = mm(2.6), mm(0.85)
        w, h = tw + 2 * px, th + 2 * py
        if draw:
            d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h / 2, fill=BROWN)
            bold_text(d, (cx - tw / 2 - b[0], y + py - b[1]), text, pill_f, WHITE, mm(0.035))
        return h

    big_f = rfont(3.8)
    note_f = rfont(2.15)

    def g_hours(y, draw=True):
        h = pill(y, "営業時間", draw) + mm(1.6)
        b, tw, th = measure(d, "AM11:00〜PM8:00", big_f, W_BIG)
        if draw:
            bold_text(d, (cx - tw / 2 - b[0], y + h - b[1]), "AM11:00〜PM8:00", big_f, BROWN, W_BIG)
        h += th + mm(1.2)
        nb, nw, nh = measure(d, "ラストオーダー PM7:30", note_f, mm(0.05))
        if draw:
            # 元のカードと同じく、時刻の右端にそろえる
            bold_text(d, (cx + tw / 2 - nw - nb[0], y + h - nb[1]), "ラストオーダー PM7:30", note_f, BROWN, mm(0.05))
        return h + nh

    def g_closed(y, draw=True):
        h = pill(y, "定休日", draw) + mm(1.6)
        b, tw, th = measure(d, "毎月15日・26日", big_f, W_BIG)
        if draw:
            bold_text(d, (cx - tw / 2 - b[0], y + h - b[1]), "毎月15日・26日", big_f, BROWN, W_BIG)
        h += th + mm(1.2)
        note = "※都合により臨時休業する場合があります"
        nb, nw, nh = measure(d, note, note_f)
        if draw:
            d.text((cx - nw / 2 - nb[0], y + h - nb[1]), note, font=note_f, fill=NOTE)
        return h + nh

    to_f = rfont(2.2)

    def g_takeout(y, draw=True):
        """お持ち帰りの案内(汁物以外)。小さい茶色の札 + 補足を1行に。"""
        tag = "お持ち帰りOK"
        rest = "（汁物以外）"
        tb, tw, th = measure(d, tag, to_f, mm(0.035))
        rb, rw, rh = measure(d, rest, to_f, mm(0.035))
        px, py = mm(1.8), mm(0.6)
        pw, ph = tw + 2 * px, th + 2 * py
        gap = mm(0.2)   # 全角カッコに余白があるので詰める
        x0 = cx - (pw + gap + rw) / 2
        if draw:
            d.rounded_rectangle((x0, y, x0 + pw, y + ph), radius=ph / 2, fill=BROWN)
            bold_text(d, (x0 + px - tb[0], y + py - tb[1]), tag, to_f, WHITE, mm(0.035))
            bold_text(d, (x0 + pw + gap - rb[0], y + (ph - rh) / 2 - rb[1]), rest, to_f, BROWN, mm(0.035))
        return ph

    addr_f = rfont(2.55)
    zip_f = rfont(2.15)

    def g_address(y, draw=True):
        b, tw, th = measure(d, "〒370-2134", zip_f, mm(0.05))
        if draw:
            bold_text(d, (cx - tw / 2 - b[0], y - b[1]), "〒370-2134", zip_f, BROWN, mm(0.05))
        h = th + mm(1.0)
        b, tw, th = measure(d, "群馬県高崎市吉井町塩川37-4", addr_f, mm(0.04))
        if draw:
            bold_text(d, (cx - tw / 2 - b[0], y + h - b[1]), "群馬県高崎市吉井町塩川37-4", addr_f, BROWN, mm(0.04))
        return h + th

    q = mm(12.0)
    lbl_f = rfont(2.1)
    q_gap = mm(8.0)

    def g_qr(y, draw=True):
        b, _, th = measure(d, "@youkiken_", lbl_f, mm(0.06))
        if not draw:
            return q + mm(1.4) + th
        for i, (url, icon, label) in enumerate(((kit.INSTA_URL, kit.icon_instagram_color, "@youkiken_"),
                                                 (kit.HP_URL, kit.icon_home, "youkiken.com"))):
            x = cx - q_gap // 2 - q + i * (q + q_gap)
            card.paste(kit.make_qr(url, q, BROWN, icon), (x, y))
            lb, lw, lh = measure(d, label, lbl_f, mm(0.06))
            ly = y + q + mm(1.4)
            qcx = x + q // 2
            if icon is kit.icon_instagram_color:
                isz, igap = round(lh * 1.35), mm(0.6)
                x0 = qcx - (isz + igap + lw) // 2
                ig = kit.icon_instagram_color(isz)
                card.paste(ig, (x0, ly + (lh - isz) // 2), ig)
                bold_text(d, (x0 + isz + igap - lb[0], ly - lb[1]), label, lbl_f, BROWN, mm(0.06))
            else:
                bold_text(d, (qcx - lw / 2 - lb[0], ly - lb[1]), label, lbl_f, BROWN, mm(0.06))
        return q + mm(1.4) + th

    groups = [g_sign, g_tel, g_hours, g_closed, g_takeout, g_address, g_qr]
    heights = [g(0, draw=False) for g in groups]
    space = CH - mm(TOP) - mm(BOTTOM) - sum(heights)
    step = space / (len(groups) - 1)
    if step < mm(2.8):
        raise SystemExit(f"収まりません(まとまりの間隔 {step / mm(1):.1f}mm)")
    y = mm(TOP)
    for g, h in zip(groups, heights):
        g(round(y))
        y += h + step

    card.save(OUT, dpi=(DPI, DPI))
    bleed = mm(3)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), WHITE)
    padded.paste(card, (bleed, bleed))
    padded.save(OUT_BLEED, dpi=(DPI, DPI))
    print(f"saved {OUT.name}  (まとまりの間隔 {step / mm(1):.1f}mm)")


if __name__ == "__main__":
    main()
