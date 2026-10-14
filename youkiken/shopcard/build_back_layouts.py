"""ショップカード裏面のレイアウト案(黄金比ベース)を4つ作る。

名刺(55×91mm)はほぼ黄金長方形なので、黄金分割の線を骨組みにする。
  縦: 91mm → 上 34.8mm : 下 56.2mm
  横: 55mm → 左 34.0mm : 右 21.0mm
文字の大きさは1.333倍刻み(1.6 → 2.1 → 2.8 → 3.8 → 5.0mm)の5段階に絞る。

  A 黄金分割(上下)  … 上38%に店名、下62%を左の情報欄と右のQR列に分ける
  B 縦書き看板      … 右21mmの列に筆文字を縦に積み、左34mmに情報
  C ミニマル左揃え  … 全部を左の1本の線に揃え、電話を黄金分割線に置く
  D キャラ主役      … まんぷくボーイを主役にし、情報は下にまとめる

使い方: python3 youkiken/shopcard/build_back_layouts.py [--guides]
  --guides を付けると黄金分割の補助線を描いた確認用画像も出す
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import build_back_v2 as kit
from build_back_v2 import CW, CH, DPI, INK, RED, WHITE, gothic, mm

HERE = Path(__file__).resolve().parent
PHI = (1 + 5 ** 0.5) / 2
GOLD_Y = 91 / PHI ** 2          # 34.8mm(上から)
GOLD_X = 55 / PHI               # 34.0mm(左から)
SUB = (110, 96, 92)
RULE = mm(0.25)

# 文字の大きさ(1.333倍刻み)
S1, S2, S3, S4, S5 = 1.6, 2.13, 2.84, 3.79, 5.05

CATCH = "名物ジャンボ餃子と自家製麺"
FOUNDED = "昭和三十六年創業"


def font(w, size_mm):
    return gothic(w, mm(size_mm))


def mincho(size_mm):
    return ImageFont.truetype(kit.MINCHO, mm(size_mm))


def size_of(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def text_at(draw, x, y, text, f, fill, anchor="l"):
    """y を文字の上端にして描く。anchor は l(左) / c(中央) / r(右)。幅と高さを返す。"""
    b = draw.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    ox = {"l": 0, "c": w / 2, "r": w}[anchor]
    draw.text((x - ox - b[0], y - b[1]), text, font=f, fill=fill)
    return w, h


def vertical_text(draw, cx, y, text, f, fill, gap_ratio=0.12):
    """1文字ずつ縦に積む(縦書き)。全体の高さを返す。"""
    cy = y
    for ch in text:
        w, h = size_of(draw, "国", f)
        b = draw.textbbox((0, 0), ch, font=f)
        cw = b[2] - b[0]
        draw.text((cx - cw / 2 - b[0], cy + (h - (b[3] - b[1])) / 2 - b[1]), ch, font=f, fill=fill)
        cy += h + h * gap_ratio
    return cy - y


def logo(size):
    return Image.open(kit.LOGO).convert("RGB").resize((size, size), Image.LANCZOS)


def brush(height):
    b = kit.brush_text(INK)
    return b.resize((round(b.width * height / b.height), height), Image.LANCZOS)


def brush_chars(width):
    """筆文字を 陽・気・軒 の3文字に分け、それぞれ幅 width にして返す。"""
    b = kit.brush_text(INK)
    a = np.asarray(b)[..., 3]
    cols = (a > 60).sum(axis=0)
    segs, inside = [], False
    for x, v in enumerate(cols):
        if v > 0 and not inside:
            inside, s = True, x
        elif v == 0 and inside:
            inside = False
            segs.append((s, x - 1))
    if inside:
        segs.append((s, len(cols) - 1))
    out = []
    for x0, x1 in segs:
        c = b.crop((x0, 0, x1 + 1, b.height))
        rows = np.where((np.asarray(c)[..., 3] > 60).any(axis=1))[0]
        c = c.crop((0, rows[0], c.width, rows[-1] + 1))
        out.append(c.resize((width, round(c.height * width / c.width)), Image.LANCZOS))
    return out


def boy(width):
    im = Image.open(kit.CHARA).convert("RGBA")
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def qr(kind, size):
    if kind == "ig":
        return kit.make_qr(kit.INSTA_URL, size, INK, kit.icon_instagram_color)
    return kit.make_qr(kit.HP_URL, size, INK, kit.icon_home)


def qr_label(card, draw, cx, y, kind, f, anchor="c"):
    """QRの下のラベル(1行)。Instagramはアイコン付き。"""
    text = "@youkiken_" if kind == "ig" else "youkiken.com"
    tw, th = size_of(draw, text, f)
    if kind != "ig":
        return text_at(draw, cx, y, text, f, INK, anchor)
    isz, gap = round(th * 1.3), mm(0.6)
    total = isz + gap + tw
    x0 = {"l": cx, "c": cx - total / 2, "r": cx - total}[anchor]
    ic = kit.icon_instagram_color(isz)
    card.paste(ic, (round(x0), round(y + (th - isz) / 2)), ic)
    text_at(draw, x0 + isz + gap, y, text, f, INK)
    return total, th


def label_value(draw, x, y, label, value, lf, vf, label_w):
    """左に赤い小見出し、右に値。値の上端に見出しの上端を合わせる。高さを返す。"""
    _, vh = size_of(draw, value, vf)
    _, lh = size_of(draw, label, lf)
    text_at(draw, x, y + (vh - lh) / 2, label, lf, RED)
    text_at(draw, x + label_w, y, value, vf, INK)
    return vh


def new_card():
    card = Image.new("RGB", (CW, CH), WHITE)
    return card, ImageDraw.Draw(card)


# ---------------------------------------------------------------- A
def layout_a():
    card, d = new_card()
    M = 5.0
    # 上 38.2%: 店名
    lg = mm(11.0)
    br = brush(round(lg * 0.88))
    gap = mm(2.2)
    row_w = lg + gap + br.width
    sub_f = mincho(S1)
    _, sub_h = size_of(d, f"{FOUNDED}　{CATCH}", sub_f)
    block_h = lg + mm(2.6) + sub_h
    top = mm(GOLD_Y - 5.5) - block_h
    x0 = (CW - row_w) // 2
    card.paste(logo(lg), (x0, top))
    card.paste(br, (x0 + lg + gap, top + (lg - br.height) // 2), br)
    text_at(d, CW / 2, top + lg + mm(2.6), f"{FOUNDED}　{CATCH}", sub_f, SUB, "c")
    # 黄金分割線(中央に21mmだけ)
    rl = mm(55 / PHI ** 2) // 2
    d.line([(CW / 2 - rl, mm(GOLD_Y)), (CW / 2 + rl, mm(GOLD_Y))], fill=RED, width=RULE)

    # 下 61.8%: 左34mmに情報、右21mmにQRを縦に2つ
    zone_top, zone_bot = mm(GOLD_Y + 5.5), CH - mm(M + 1.5)
    q = mm(14.5)
    lf = font(6, S1)
    qcx = round(mm(GOLD_X + (55 - GOLD_X - M) / 2))
    q_lbl_h = size_of(d, "@youkiken_", lf)[1]
    unit = q + mm(1.2) + q_lbl_h
    qy = zone_top
    q_gap = zone_bot - zone_top - 2 * unit
    for i, kind in enumerate(("ig", "hp")):
        y = qy + i * (unit + q_gap)
        card.paste(qr(kind, q), (qcx - q // 2, y))
        qr_label(card, d, qcx, y + q + mm(1.2), kind, lf)
    span_top, span_bot = qy, qy + 2 * unit + q_gap

    x = mm(M)
    lbl = font(6, S1)
    items = []

    def tel(y, dry):
        dd = d if not dry else ImageDraw.Draw(Image.new("RGB", (1, 1)))
        h = text_at(dd, x, y, "TEL", lbl, RED)[1] + mm(0.9)
        return h + text_at(dd, x, y + h, "027-387-7082", font(7, S3 * 1.1), INK)[1]

    def hours(y, dry):
        dd = d if not dry else ImageDraw.Draw(Image.new("RGB", (1, 1)))
        h = text_at(dd, x, y, "営業時間", lbl, RED)[1] + mm(0.9)
        h += text_at(dd, x, y + h, "11:00 – 20:00", font(7, S3), INK)[1] + mm(0.7)
        return h + text_at(dd, x, y + h, "ラストオーダー 19:30", font(5, S1), SUB)[1]

    def closed(y, dry):
        dd = d if not dry else ImageDraw.Draw(Image.new("RGB", (1, 1)))
        h = text_at(dd, x, y, "定休日", lbl, RED)[1] + mm(0.9)
        return h + text_at(dd, x, y + h, "毎月15日・26日", font(7, S3), INK)[1]

    def address(y, dry):
        dd = d if not dry else ImageDraw.Draw(Image.new("RGB", (1, 1)))
        h = text_at(dd, x, y, "所在地", lbl, RED)[1] + mm(0.9)
        h += text_at(dd, x, y + h, "〒370-2134", font(5, S1), SUB)[1] + mm(0.7)
        h += text_at(dd, x, y + h, "群馬県高崎市吉井町", font(6, S2), INK)[1] + mm(0.6)
        return h + text_at(dd, x, y + h, "塩川37-4", font(6, S2), INK)[1]

    items = [tel, hours, closed, address]
    hs = [it(0, True) for it in items]
    step = (span_bot - span_top - sum(hs)) / (len(items) - 1)
    y = span_top
    for it, h in zip(items, hs):
        it(round(y), False)
        y += h + step
    # 情報欄とQR列の間の細い縦線(黄金分割線)
    d.line([(mm(GOLD_X), span_top), (mm(GOLD_X), span_bot)], fill=(225, 210, 205), width=RULE)
    return card


# ---------------------------------------------------------------- B
def layout_b():
    card, d = new_card()
    M = 5.0
    col_x0 = mm(GOLD_X)
    col_cx = round((col_x0 + CW - mm(M)) / 2) + mm(0.8)
    # 右の列: 縦書きの小見出し + 筆文字3文字 + 落款のようにロゴ
    chars = brush_chars(mm(11.0))
    y = mm(7.0)
    for c in chars:
        card.paste(c, (col_cx - c.width // 2, y), c)
        y += c.height + mm(1.6)
    brush_bottom = y - mm(1.6)
    lg = mm(9.0)
    seal_y = brush_bottom + mm(3.2)
    card.paste(logo(lg), (col_cx - lg // 2, seal_y))
    vertical_text(d, col_x0 + mm(1.6), mm(7.0), FOUNDED, mincho(S1 * 0.95), SUB)
    d.line([(col_x0, mm(7.0)), (col_x0, seal_y + lg)], fill=RED, width=RULE)
    # 右下: まんぷくボーイ
    by = boy(mm(16.5))
    card.paste(by, (CW - mm(M) - by.width, CH - mm(M + 1.5) - by.height), by)

    # 左の列: QR 2つを下に置き、その上の空間に情報を均等に並べる
    x = mm(M)
    lbl = font(6, S1)
    q = mm(12.0)
    lf = font(6, S1 * 0.92)
    lbl_h = size_of(d, "@youkiken_", lf)[1]
    qy = CH - mm(M + 1.0) - lbl_h - mm(1.0) - q
    for i, kind in enumerate(("ig", "hp")):
        qx = mm(M) + i * (q + mm(3.5))
        card.paste(qr(kind, q), (qx, qy))
        qr_label(card, d, qx + q // 2, qy + q + mm(1.0), kind, lf)

    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def catch(dd, y):
        return text_at(dd, x, y, CATCH, font(6, S1 * 1.02), RED)[1]

    def tel(dd, y):
        h = text_at(dd, x, y, "TEL", lbl, RED)[1] + mm(0.9)
        return h + text_at(dd, x, y + h, "027-387-7082", font(7, S3 * 1.08), INK)[1]

    def times(dd, y):
        h = label_value(dd, x, y, "営業", "11:00 – 20:00", lbl, font(7, S2 * 1.1), mm(6.0)) + mm(0.8)
        h += text_at(dd, x + mm(6.0), y + h, "ラストオーダー 19:30", font(5, S1 * 0.95), SUB)[1] + mm(2.6)
        return h + label_value(dd, x, y + h, "定休", "毎月15日・26日", lbl, font(7, S2 * 1.1), mm(6.0))

    def address(dd, y):
        h = text_at(dd, x, y, "〒370-2134", font(5, S1), SUB)[1] + mm(0.8)
        return h + text_at(dd, x, y + h, "群馬県高崎市吉井町塩川37-4", font(6, S2 * 0.86), INK)[1]

    items = [catch, tel, times, address]
    hs = [it(scratch, 0) for it in items]
    top, bot = mm(7.0), qy - mm(6.0)
    step = (bot - top - sum(hs)) / (len(items) - 1)
    y = top
    for it, h in zip(items, hs):
        it(d, round(y))
        y += h + step
    return card


# ---------------------------------------------------------------- C
def layout_c():
    card, d = new_card()
    X = mm(7.0)
    lbl = font(6, S1)
    # ヘッダー: ロゴ + 筆文字(小さめ)を左に
    lg = mm(8.0)
    card.paste(logo(lg), (X, mm(8.0)))
    br = brush(round(lg * 0.85))
    card.paste(br, (X + lg + mm(2.0), mm(8.0) + (lg - br.height) // 2), br)
    text_at(d, X, mm(8.0) + lg + mm(2.2), f"{FOUNDED}　{CATCH}", mincho(S1 * 0.95), SUB)
    # 黄金分割線上に電話
    d.line([(X, mm(GOLD_Y) - mm(4.0)), (X + mm(8.0), mm(GOLD_Y) - mm(4.0))], fill=RED, width=RULE)
    y = mm(GOLD_Y) - mm(1.6)
    y += text_at(d, X, y, "TEL", lbl, RED)[1] + mm(1.0)
    y += text_at(d, X, y, "027-387-7082", font(7, S5), INK)[1] + mm(7.0)
    # 定義リスト
    LW = mm(9.5)
    vf = font(6, S2)
    y += label_value(d, X, y, "営業時間", "11:00 – 20:00", lbl, font(7, S2 * 1.15), LW) + mm(0.9)
    y += text_at(d, X + LW, y, "ラストオーダー 19:30", font(5, S1), SUB)[1] + mm(3.4)
    y += label_value(d, X, y, "定休日", "毎月15日・26日", lbl, font(7, S2 * 1.15), LW) + mm(3.4)
    y += label_value(d, X, y, "所在地", "〒370-2134", lbl, font(5, S1 * 1.05), LW) + mm(0.9)
    text_at(d, X + LW, y, "群馬県高崎市吉井町塩川37-4", vf, INK)
    # 下: QRを左揃えで2つ、ラベルはQRの下
    q = mm(11.5)
    lf = font(6, S1 * 0.9)
    lbl_h = size_of(d, "@youkiken_", lf)[1]
    by = CH - mm(7.0) - lbl_h - mm(1.0) - q
    for i, kind in enumerate(("ig", "hp")):
        qx = X + i * (q + mm(6.0))
        card.paste(qr(kind, q), (qx, by))
        qr_label(card, d, qx, by + q + mm(1.0), kind, lf, "l")
    return card


# ---------------------------------------------------------------- D
def layout_d():
    card, d = new_card()
    # 上: ロゴ+筆文字を小さく
    lg = mm(7.5)
    br = brush(round(lg * 0.88))
    gap = mm(1.8)
    row_w = lg + gap + br.width
    x0 = (CW - row_w) // 2
    top = mm(6.5)
    card.paste(logo(lg), (x0, top))
    card.paste(br, (x0 + lg + gap, top + (lg - br.height) // 2), br)
    # 主役: まんぷくボーイを黄金分割線の上に大きく
    by = boy(mm(34.0))
    boy_y = top + lg + mm(2.5)
    card.paste(by, ((CW - by.width) // 2, boy_y), by)
    y = boy_y + by.height + mm(1.8)
    y += text_at(d, CW / 2, y, CATCH, font(6, S2), RED, "c")[1] + mm(1.0)
    y += text_at(d, CW / 2, y, FOUNDED, mincho(S1), SUB, "c")[1] + mm(5.0)
    # 情報
    y += text_at(d, CW / 2, y, "027-387-7082", font(7, S4), INK, "c")[1] + mm(2.8)
    y += text_at(d, CW / 2, y, "11:00 – 20:00（L.O. 19:30）", font(6, S2 * 0.95), INK, "c")[1] + mm(1.1)
    y += text_at(d, CW / 2, y, "定休日　毎月15日・26日", font(6, S2 * 0.95), INK, "c")[1] + mm(1.1)
    text_at(d, CW / 2, y, "群馬県高崎市吉井町塩川37-4", font(5, S1 * 1.05), SUB, "c")
    # 下: QR 2つ
    q = mm(11.0)
    lf = font(6, S1 * 0.9)
    lbl_h = size_of(d, "@youkiken_", lf)[1]
    qy = CH - mm(5.5) - lbl_h - mm(1.0) - q
    gapq = mm(9.0)
    for i, kind in enumerate(("ig", "hp")):
        qx = CW // 2 - gapq // 2 - q + i * (q + gapq)
        card.paste(qr(kind, q), (qx, qy))
        qr_label(card, d, qx + q // 2, qy + q + mm(1.0), kind, lf)
    return card


def guides(card):
    g = card.copy()
    d = ImageDraw.Draw(g)
    c = (0, 160, 255)
    w = max(2, mm(0.15))
    for y in (mm(GOLD_Y), CH - mm(GOLD_Y)):
        d.line([(0, y), (CW, y)], fill=c, width=w)
    for x in (mm(GOLD_X), CW - mm(GOLD_X)):
        d.line([(x, 0), (x, CH)], fill=c, width=w)
    return g


def main():
    show_guides = "--guides" in sys.argv
    cards = {"A": layout_a(), "B": layout_b(), "C": layout_c(), "D": layout_d()}
    for name, card in cards.items():
        card.save(HERE / f"back_alt_{name}.png", dpi=(DPI, DPI))
        print("saved", f"back_alt_{name}.png")
    if show_guides:
        for name, card in cards.items():
            guides(card).save(HERE / f"back_alt_{name}_guides.png", dpi=(DPI, DPI))


if __name__ == "__main__":
    main()
